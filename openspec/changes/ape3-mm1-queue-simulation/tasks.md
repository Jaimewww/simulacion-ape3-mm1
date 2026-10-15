# Tasks: APE 003 — M/M/1 queue simulation with SimPy

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1 400 – 1 900 (additions + deletions, authored) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 → PR 5 → PR 6 |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Foundation: packaging + public package shell (Phase 1) | PR 1 | `python -m pytest -q` | `python -m pip install -e . && python -m mm1 --help` | `requirements.txt`, `pyproject.toml`, `src/mm1/__init__.py`, `src/mm1/__main__.py` |
| 2 | Theory oracle (Phase 2) | PR 2 | `python -m pytest tests/test_metrics.py -q` | `python -c "from mm1.metrics import theoretical_metrics as t; print(t(2.0,3.0))"` | `src/mm1/metrics.py`, `tests/test_metrics.py` |
| 3 | Simulation engine + CLI (Phase 3) | PR 3 | `python -m pytest tests/test_simulation.py tests/test_smoke.py -q` | `python -m mm1 --replications 5 --sim-time 300 --out outputs/` | `src/mm1/simulation.py`, `src/mm1/cli.py`, both test modules |
| 4 | Scenarios + analysis (Phase 4) | PR 4 | `python -m pytest tests/test_scenarios.py tests/test_analysis.py -q` | `python -c "from mm1.scenarios import run_scenarios; from mm1.analysis import summarize; print(len(summarize(run_scenarios(replications=3, sim_time=100.0))))"` | `src/mm1/scenarios.py`, `src/mm1/analysis.py`, both test modules |
| 5 | Tables + charts (Phase 5) | PR 5 | `python -m pytest tests/test_tables.py tests/test_charts.py -q` | `python -m mm1 --replications 5 --sim-time 300 --out outputs/ && ls outputs/` | `src/mm1/tables.py`, `src/mm1/charts.py`, both test modules |
| 6 | Streamlit resource + document (Phase 6) | PR 6 | `python -m pytest tests/test_app.py -q` | `streamlit run app/streamlit_app.py` (manual, no browser runner) | `app/streamlit_app.py`, `tests/test_app.py`, `reports/**` |

Merge order: PR 1 → PR 2 → PR 3 → PR 4 → PR 5 → PR 6. Slices are file-disjoint and
can be *developed* in parallel, but each PR's integration tests only reach GREEN
once its upstream interfaces exist. All PRs target `main`.

## Phase 1: Shared Foundation (orchestrator) — must land first

Note: `python -m mm1` and `import mm1` outside pytest need an editable install
(`python -m pip install -e .`) because pytest alone gets `src/` from
`pythonpath`. Verify with the venv interpreter the team actually runs.

- [ ] 1.1 `requirements.txt`: pin `simpy`, `numpy`, `matplotlib`, `pandas`, `streamlit`, `pytest`, `pytest-cov`, `ruff`. Interface: installable dependency set for `mm1`. Acceptance: `python -m pip install -r requirements.txt` succeeds and `python -m pytest --version` works. Specs: S2, S12.
- [ ] 1.2 `pyproject.toml`: `src/` layout, package `mm1`, pytest `pythonpath = ["src"]`, ruff config, `[tool.pytest.ini_options] testpaths = ["tests"]`, installable with `pip install -e .`. Interface: `import mm1` resolves from `src/`. Acceptance: `python -m pip install -e .` succeeds, `python -c "import mm1"` exits 0, and `python -m ruff check src` exits 0. Specs: S2, S12.
- [ ] 1.3 `src/mm1/__init__.py`: re-export every frozen public name (`TheoryMetrics`, `utilization`, `is_stable`, `theoretical_metrics`, `CustomerRecord`, `ScenarioRun`, `run_mm1`, `Scenario`, `SCENARIOS`, `run_scenarios`, `ScenarioSummary`, `confidence_interval`, `relative_error`, `summarize`, `comparison_dataframe`, `write_csv`, `to_latex`, the four `plot_*`, `generate_all`, `main`) with `__all__`. Interface: design.md public contract. Acceptance: `python -c "import mm1; assert len(mm1.__all__) >= 20"` exits 0. Specs: S2, S14.
- [ ] 1.4 `src/mm1/__main__.py` (3-line shim to `cli.main`, decision D11) and `.gitignore` entries for `outputs/` and `.atl/`. Interface: `python -m mm1` entry point. Acceptance: after 1.2, `python -m mm1 --help` exits 0 from the repository root (both the editable install and this shim are required; the shim alone is not enough). Specs: S2, S12, S13.

## Phase 2: Richard Chamba — Theory Oracle Slice (PR 2)

- [ ] 2.1 `tests/test_metrics.py` (RED): analytic values for `(2.0, 3.0)`, `(2.5, 3.0)`, `(2.9, 3.0)`; `rho < 1`; `is_stable` True/False at `lam == mu`; `ValueError` when unstable; frozen-dataclass mutation raises. Interface: `utilization`, `is_stable`, `theoretical_metrics`, `TheoryMetrics`. Acceptance: `python -m pytest tests/test_metrics.py -q` fails before 2.2. Specs: S3.
- [ ] 2.2 `src/mm1/metrics.py` (GREEN): `rho = lam / mu`, guide formulas for `L`, `Lq`, `W`, `Wq`, stability guard (decision D1, D2). Interface: as above. Acceptance: `python -m pytest tests/test_metrics.py -q` passes. Specs: S3, S4.
- [ ] 2.3 `tests/test_metrics.py` (PRESERVE): one test per touched behavior — exact guide formulas `L = lam/(mu-lam)`, `W = 1/(mu-lam)`, and `is_stable(2.9, 3.0) is True`. Acceptance: passes without further code change. Specs: S3, S5.
- [ ] 2.4 `src/mm1/metrics.py` (REFACTOR): extract a single tolerance constant; focused tests stay green. Acceptance: `python -m pytest tests/test_metrics.py -q` still passes. Specs: S3.

## Phase 3: Jaime Landazuri — Simulation Engine + CLI Slice (PR 3)

- [ ] 3.1 `tests/test_simulation.py` (RED): single-server serialization, FIFO order, record identities (`wait_time == service_start - arrival_time`), non-empty monotonic `queue_trace`, seed determinism, warmup exclusion with full `n_customers`, `ValueError` when `lam >= mu`. Interface: `run_mm1`, `CustomerRecord`, `ScenarioRun`. Acceptance: `python -m pytest tests/test_simulation.py -q` fails before 3.2. Specs: S4, S6, S7.
- [ ] 3.2 `src/mm1/simulation.py` (GREEN): SimPy environment, `capacity = 1`, exponential arrivals/service, FIFO, queue trace, statistics over `arrival_time >= warmup`. Interface: design.md signatures. Acceptance: `python -m pytest tests/test_simulation.py -q` passes. Specs: S4, S7.
- [ ] 3.3 `tests/test_smoke.py` (RED→GREEN): `python -c "import mm1"` equivalent plus `cli.main(["--lam", "2.0", "--mu", "3.0", "--out", str(tmp_path), "--sim-time", "200"]) == 0`, `main(["--lam", "3.0", "--mu", "3.0"]) != 0` with stdout `El sistema no es estable`, and that no file is written on refusal. Interface: `main(argv) -> int`. Acceptance: `python -m pytest tests/test_smoke.py -q` passes. Specs: S4, S12, S13.
- [ ] 3.4 `src/mm1/cli.py` (GREEN): `argparse` with `--lam --mu --scenarios --replications --sim-time --seed --warmup --out`; prints `El sistema no es estable` for `lam >= mu`; exit `0` on success. Interface: `main(argv: Sequence[str] | None = None) -> int`. Acceptance: `python -m mm1 --replications 5 --sim-time 300 --out outputs/` exits 0. Specs: S4, S6, S7.
- [ ] 3.5 `tests/test_simulation.py` (PRESERVE): one test per touched behavior — `sim_time` bound respected (no departure after `sim_time`) and default `seed=None` still returns a valid run. Acceptance: passes unchanged. Specs: S4, S7.
- [ ] 3.6 `src/mm1/simulation.py` + `src/mm1/cli.py` (REFACTOR): deduplicate statistics and argument parsing; both focused modules stay green. Acceptance: `python -m pytest tests/test_simulation.py tests/test_smoke.py -q` passes. Specs: S4, S7.

## Phase 4: Richard Chamba — Scenarios + Analysis Slice (PR 4)

- [ ] 4.1 `tests/test_scenarios.py` (RED): `SCENARIOS` ids/lam/mu/label/condition verbatim (S5); `run_scenarios(replications=3)` returns 9 runs ordered `1,1,1,2,2,2,3,3,3`; identical `base_seed` yields identical `seed` and `mean_wait`. Interface: `Scenario`, `SCENARIOS`, `run_scenarios`. Acceptance: `python -m pytest tests/test_scenarios.py -q` fails before 4.2. Specs: S4, S5, S6.
- [ ] 4.2 `src/mm1/scenarios.py` (GREEN): guide scenario tuples, deterministic seed derivation from `(base_seed, scenario, replication)`. Interface: as above. Acceptance: `python -m pytest tests/test_scenarios.py -q` passes. Specs: S5, S6.
- [ ] 4.3 `tests/test_analysis.py` (RED): one summary per scenario in id order, `theory == theoretical_metrics(lam, mu)`, `confidence_interval([1.0, 2.0, 3.0]) == (1.0, 3.0)`, `relative_error` cases, `summarize([])` raises `ValueError`, plus one integration test `run_scenarios(replications=3, sim_time=100.0)` → `summarize` over locally frozen fixtures where the engine is not needed. Interface: `ScenarioSummary`, `confidence_interval`, `relative_error`, `summarize`. Acceptance: `python -m pytest tests/test_analysis.py -q` fails before 4.4. Specs: S6, S7.
- [ ] 4.4 `src/mm1/analysis.py` (GREEN): grouping, t-distribution CI95, absolute relative error, four `rel_error_*` fields. Interface: design.md signatures. Acceptance: `python -m pytest tests/test_analysis.py -q` passes. Specs: S6, S7.
- [ ] 4.5 `tests/test_analysis.py` (PRESERVE) + REFACTOR: one test for `confidence_interval` default `confidence = 0.95`; extract a shared grouping helper while focused tests stay green. Acceptance: `python -m pytest tests/test_scenarios.py tests/test_analysis.py -q` passes. Specs: S6, S7.

## Phase 5: Cael Soto — Tables + Charts Slice (PR 5)

- [ ] 5.1 `tests/test_tables.py` (RED): exact 19-column schema, 3 rows in scenario order, numeric dtypes, `ci95_low <= ci95_high`, `write_csv`/`to_latex` return existing non-empty `Path`s in `tmp_path`, CSV round-trips, LaTeX contains a table environment. Interface: `comparison_dataframe`, `write_csv`, `to_latex`. Acceptance: `python -m pytest tests/test_tables.py -q` fails before 5.2. Specs: S6.
- [ ] 5.2 `src/mm1/tables.py` (GREEN): comparison frame with theory + simulated + CI + relative error columns; CSV and LaTeX writers. Interface: as above. Acceptance: `python -m pytest tests/test_tables.py -q` passes. Specs: S6, S7.
- [ ] 5.3 `tests/test_charts.py` (RED): force `matplotlib.use("Agg")`; each plot function returns an existing non-empty PNG-signature file in `tmp_path`; `generate_all` returns every path inside `out_dir` with each summary figure once. Interface: `plot_queue_evolution`, `plot_wait_times`, `plot_theory_vs_sim`, `plot_scenario_comparison`, `generate_all`. Acceptance: `python -m pytest tests/test_charts.py -q` fails before 5.4. Specs: S6, S7.
- [ ] 5.4 `src/mm1/charts.py` (GREEN): four figures (queue evolution, wait times, theory vs simulation, scenario comparison) plus `generate_all` naming files per scenario. Interface: as above. Acceptance: `python -m pytest tests/test_charts.py -q` passes. Specs: S6, S7.
- [ ] 5.5 `tests/test_charts.py` (PRESERVE) + REFACTOR: one test that repeated calls overwrite deterministically without duplicate files; share the figure-saving helper. Acceptance: `python -m pytest tests/test_tables.py tests/test_charts.py -q` passes; `python -m mm1 --replications 5 --sim-time 300 --out outputs/` then `ls outputs/` lists CSV, TeX and PNG artifacts. Specs: S6, S7.

## Phase 6: Domenica Rojas — Streamlit Resource + Document Slice (PR 6)

- [ ] 6.1 `tests/test_app.py` (RED, decision D12): `theory_row(2.0, 3.0)` maps to `theoretical_metrics(2.0, 3.0)`; `stability_message(3.0, 3.0)` reports unstable and `stability_message(2.0, 3.0)` stable; `scenario_table(summaries)` has one row per scenario; `build_queue_figure`/`build_comparison_figure` return `Figure` objects. Interface: design.md app helpers. Acceptance: `python -m pytest tests/test_app.py -q` fails before 6.2. Specs: S11, S15.
- [ ] 6.2 `app/streamlit_app.py` (GREEN): importable helpers plus `st.slider` for `lambda` and `mu`, `rho` + stability guard via `st.warning`/`st.error`, run button (`st.button`), queue evolution animation over `queue_trace`, live theory-vs-simulation table (`st.dataframe`), and at least two interactive charts (`st.line_chart` and a Matplotlib figure). Interface: design.md app contract; imports `mm1` from the repo root. Acceptance: `python -m pytest tests/test_app.py -q` passes and `streamlit run app/streamlit_app.py` starts without import errors. Specs: S11, S15.
- [ ] 6.3 `app/streamlit_app.py` (PRESERVE): one test proving the app never runs a simulation for unstable input (guard returns before `run_mm1`). Acceptance: `python -m pytest tests/test_app.py -q` passes. Specs: S11, S15.
- [ ] 6.4 `reports/` document skeleton: title, objectives, theoretical model with the `rho = lambda / mu` deviation note (D1), methodology/procedure, closed with the 3-scenario setup. Acceptance: sections 1–3 present and the deviation note cites design decision D1. Specs: S3, S9.
- [ ] 6.5 `reports/` results section: theory-vs-simulation table for the three scenarios plus the generated figures and the `python -m mm1 --out outputs` command that reproduces them. Acceptance: every figure referenced exists in `reports/figures/` and is produced by the command. Specs: S6, S7, S9.
- [ ] 6.6 `reports/` control questions: answers to the 10 guide §7 questions, three of them quoted verbatim. Acceptance: 10 numbered answers, each citing simulated evidence. Specs: S8.
- [ ] 6.7 `reports/` conclusions tied to the practice objectives and to guide §6 expected behavior (wait time and queue grow as `lambda` approaches `mu`). Acceptance: each objective has a conclusion with numbers. Specs: S7, S9.
- [ ] 6.8 `reports/` demo video link + oral-defense notes (model, code walkthrough, expected questions). Acceptance: video URL present and reachable, defense notes reference `design.md` decisions. Specs: S9.

## Phase 7: Integration, Verification and Archive Prep (post-apply)

- [ ] 7.1 Full suite: `python -m pytest -q` green and `python -m ruff check src tests app` clean. Specs: S2, S14.
- [ ] 7.2 Regeneration check: `python -m mm1 --out outputs/` reproduces every table and figure used by the report; no manual editing of `outputs/`. Specs: S7.
- [ ] 7.3 Coherence check: guide §5.1 → `design.md` D1 → `tests/test_metrics.py` all state `rho = lambda / mu`. Specs: S3.
- [ ] 7.4 Guide↔plan traceability sweep: every S1–S15 id appears in at least one spec and one task. Specs: S1–S15.
- [ ] 7.5 Run `sdd-verify`, then `sdd-archive` to merge the four deltas into `openspec/specs/`. Specs: S13.

## Branch / PR Policy per Member

| Member | Slice | Branch | PR target | Owned files |
|--------|-------|--------|-----------|-------------|
| Orchestrator | Foundation (PR 1) | `feat/orchestrator-foundation` | `main` | `requirements.txt`, `pyproject.toml`, `.gitignore`, `README.md`, `src/mm1/__init__.py`, `src/mm1/__main__.py` |
| Richard Chamba | Theory (PR 2) + Scenarios/Analysis (PR 4) | `feat/richard-theory-analysis` | `main` | `src/mm1/metrics.py`, `src/mm1/scenarios.py`, `src/mm1/analysis.py`, `tests/test_metrics.py`, `tests/test_scenarios.py`, `tests/test_analysis.py` |
| Jaime Landazuri | Simulation + CLI (PR 3) | `feat/jaime-simulation-cli` | `main` | `src/mm1/simulation.py`, `src/mm1/cli.py`, `tests/test_simulation.py`, `tests/test_smoke.py` |
| Cael Soto | Tables + Charts (PR 5) | `feat/cael-tables-charts` | `main` | `src/mm1/tables.py`, `src/mm1/charts.py`, `tests/test_tables.py`, `tests/test_charts.py`, `reports/figures/**` |
| Domenica Rojas | Streamlit + Document (PR 6) | `feat/domenica-streamlit-document` | `main` | `app/streamlit_app.py`, `tests/test_app.py`, `reports/**` |

Rules: one slice per PR; no edits outside the owned files; each PR ships code plus
its tests plus the docs it invalidates; `python -m pytest -q` and
`python -m ruff check src tests app` must be green before review; keep authored
changes under 400 lines per PR (TDD tests, code and docs stay in the same PR).

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High
