# Delta for mm1-reporting

## ADDED Requirements

### Requirement: Analysis MUST summarize replications per scenario

`summarize(runs)` MUST accept `ScenarioRun` objects from one or more scenarios and
return one frozen `ScenarioSummary` per scenario id, ordered by scenario id. Each
summary MUST carry `scenario`, `lam`, `mu`, `replications`, `theory` (a
`TheoryMetrics`), `sim_mean_wait`, `sim_mean_queue`, `sim_mean_in_system`,
`sim_utilization`, `std_wait`, `ci95_wait`, and `rel_error_L`, `rel_error_Lq`,
`rel_error_W`, `rel_error_Wq` computed against theory. `confidence_interval(values,
confidence=0.95)` MUST return the two-sided Student-t interval **of the mean**,
`mean ± t((1+confidence)/2, n-1) · s / √n`, where `s` is the sample standard
deviation with `ddof=1` and `n = len(values)`. It MUST raise `ValueError` for empty
input or for a `confidence` outside `(0, 1)`, and MUST return `(value, value)` when
`len(values) == 1`, because a single observation carries no dispersion.
`ci95_wait` MUST be that interval computed over the **per-replication `mean_wait`
values**, never over individual customer waits: the quantity being compared against
the theory is the mean of the simulated means. The implementation MUST use the
standard library only; SciPy is not a dependency of this project.
`relative_error(simulated, theoretical)` MUST return
`abs(simulated - theoretical) / abs(theoretical)` and MUST raise `ValueError` when
`theoretical == 0`. Specs: S6, S7.

#### Scenario: One summary per scenario

- GIVEN runs produced by `run_scenarios(replications=3, sim_time=100.0)`
- WHEN `summarize(runs)` is called
- THEN 3 summaries are returned with scenario ids `1, 2, 3`
- AND each `replications == 3`
- AND each `theory` equals `theoretical_metrics(lam, mu)`

#### Scenario: Confidence interval and relative error are correct

- GIVEN `values = [1.0, 2.0, 3.0]`
- WHEN `confidence_interval(values)` is called
- THEN the result is `(-0.4841, 4.4841)` within `1e-4`, which is
  `2.0 ± 4.302653 · 1.0 / √3` with `t(0.975, 2) = 4.302653`
- AND the interval is wider than the sample range `[1, 3]`, as expected for `n = 3`
- AND `confidence_interval([7.0]) == (7.0, 7.0)`
- AND `confidence_interval([])` raises `ValueError`
- GIVEN `relative_error(1.05, 1.0)` and `relative_error(0.0, 1.0)`
- THEN the results are `0.05` and `1.0` respectively
- AND `relative_error(1.0, 0.0)` raises `ValueError`

#### Scenario: Empty input is rejected

- GIVEN an empty sequence of runs
- WHEN `summarize([])` is called
- THEN it raises `ValueError` and no summary is returned

### Requirement: The comparison table MUST expose theory vs simulation

`comparison_dataframe(summaries)` MUST return a `pandas.DataFrame` with exactly one
row per scenario and the columns `scenario, lam, mu, rho, L, Lq, W, Wq,
sim_mean_wait, sim_mean_queue, sim_mean_in_system, sim_utilization, std_wait,
ci95_low, ci95_high, rel_error_L, rel_error_Lq, rel_error_W, rel_error_Wq`; row
order follows scenario id and every value column is numeric. This table satisfies
the guide requirement "comparar los resultados mediante una tabla". Spec: S6.

#### Scenario: Table shape and ordering

- GIVEN summaries for the three guide scenarios
- WHEN `comparison_dataframe(summaries)` is called
- THEN the frame has 3 rows and the exact column list above
- AND `rho`, `L`, `Lq`, `W`, `Wq` come from the theoretical model
- AND `ci95_low <= ci95_high`

#### Scenario: CSV and LaTeX exports are written to disk

- GIVEN the comparison frame and a temporary directory
- WHEN `write_csv(df, path)` and `to_latex(df, path)` are called
- THEN both return `Path` objects that exist and are non-empty
- AND the CSV re-reads with the same columns and 3 rows
- AND the LaTeX file contains a bookmarkable table environment

### Requirement: Charts MUST visualize queue, waits, and theory vs simulation

`charts` MUST provide `plot_queue_evolution(run, path)`, `plot_wait_times(run,
path)`, `plot_theory_vs_sim(summaries, path)`, `plot_scenario_comparison(summaries,
path)` and `generate_all(runs, summaries, out_dir)`. Each plot function MUST write
a non-empty `Path` and MUST NOT require an interactive display. `generate_all`
MUST write the figures for every run plus the two summary figures and return the
list of created paths. Specs: S6, S7.

#### Scenario: Queue and wait charts are produced

- GIVEN one completed stable run
- WHEN `plot_queue_evolution(run, path)` and `plot_wait_times(run, path)` are called
- THEN both files exist, are non-empty, and start with the PNG signature

#### Scenario: Theory-vs-simulation and comparison charts are produced

- GIVEN summaries for the three guide scenarios
- WHEN `plot_theory_vs_sim` and `plot_scenario_comparison` are called
- THEN both PNG files exist and are non-empty

#### Scenario: generate_all returns every figure path

- GIVEN 3 runs and their summaries with a temporary output directory
- WHEN `generate_all(runs, summaries, out_dir)` is called
- THEN every returned path exists inside `out_dir`
- AND the two summary figures are each returned exactly once
