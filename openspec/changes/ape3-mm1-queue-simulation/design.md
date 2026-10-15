# Design: APE 003 — M/M/1 queue simulation with SimPy

## Technical Approach

One Python package, `src/mm1`, built theory-first. `metrics.py` implements the
guide §5.1 formulas and becomes the correctness oracle for the simulator.
`simulation.py` runs the SimPy `λ >= μ` guard and the FIFO single-server process,
emitting immutable records and a queue trace. `scenarios.py` declares the three
guide scenarios as data and drives replicas. `analysis.py` aggregates replicas
into summaries with CI95 and relative error. `tables.py` and `charts.py` render
the guide's comparison table and figures. `cli.py` orchestrates the whole pipeline
(`python -m mm1`), and `app/streamlit_app.py` exposes the same functions through an
interactive Streamlit resource with no duplicated simulation logic.

Satisfies the proposal approach for `mm1-theory`, `mm1-simulation`,
`mm1-reporting` and `mm1-delivery`.

## Architecture Decisions

| # | Choice | Alternatives considered | Rationale |
|---|--------|-------------------------|-----------|
| D1 | `rho = lam / mu` | Guide §5.1 literal `rho = mu / lam` | Guide's own stability condition is `lam < mu`; `mu / lam` would give `rho > 1` for all three scenarios (1.5, 1.2, 1.03) and contradict `L`, `Lq`, `W`, `Wq`, which are only valid for `lam < mu`. Documented deviation, required by guide §5.1 pseudocode which itself computes `ρ = λ / μ`. |
| D2 | `theoretical_metrics` and `run_mm1` raise `ValueError` when `lam >= mu` | Return `inf`/`nan`; return `None` | Guide pseudocode branches on `SI λ >= μ` before computing anything; failing fast keeps the CLI guard and the library guard identical. |
| D3 | Frozen dataclasses (`TheoryMetrics`, `CustomerRecord`, `ScenarioRun`, `Scenario`, `ScenarioSummary`) | Mutable dicts / plain classes | Prevents accidental mutation across summary aggregation and enables equality-based test assertions. |
| D4 | Deterministic per-run seeds derived from `base_seed` and `(scenario, replication)` | One global `numpy` seed | Reproducible evidence for the report and independent replicas per scenario; a global seed makes scenario ordering significant. |
| D5 | `warmup` filters statistics but keeps full records, default `0.0` | Discard warmup customers; ignore warmup | Default `0.0` preserves the guide behavior exactly, while analysis can exclude start-up bias; keeping records lets the report show the transient. |
| D6 | `pandas` for tables and `matplotlib` (`Agg`) for charts | Hand-rolled CSV; `seaborn`; `plotly` | Guide §3 lists NumPy/Matplotlib; `pandas` centralizes the table and gives `to_latex` for the report; `Agg` keeps charts headless and test-safe. |
| D7 | Streamlit for the interactive resource | Jupyter notebook (`ipywidgets`); Plotly Dash | User decision S15; Streamlit gives sliders, live tables and charts from the existing functions with the least glue code. |
| D8 | `python -m mm1` as the single orchestration entry point | Scripts per stage; Makefile | The demo video and the report need one reproducible command; CLI flags cover the manual single-`lam`/`mu` probe. |
| D9 | Four disjoint member slices, one PR each | One shared branch per feature area | S14 needs four AI agents working in parallel with no merge conflicts; each slice owns whole files. |
| D10 | App helpers as importable pure functions tested without Streamlit | Streamlit AppTest E2E only | No browser runner is planned; pure helpers (`theory_row`, `stability_message`, `scenario_table`, `build_queue_figure`, `build_comparison_figure`) are unit-testable. |
| D11 | Add `src/mm1/__main__.py` as a 3-line shim (`from mm1.cli import main; raise SystemExit(main())`), and require an editable install | Declare a `mm1` console script in `pyproject.toml`; drop `python -m mm1`; put the dispatch inside `__init__.py` | The frozen map lists only `__init__.py` and `cli.py`, but `python -m mm1` (frozen entry point) is only executable through `mm1/__main__.py`, and `src/` is only importable outside pytest after `pip install -e .` (observed: `.venv/bin/python -m mm1 --help` fails with `No module named mm1` in the current skeleton, which has neither). This is the smallest addition that keeps the frozen entry point working; the dispatch logic still lives in `cli.main`, so the public contract is unchanged. Flagged as an open question for the orchestrator. |
| D12 | Add `tests/test_app.py` for the app helpers | Put app-helper tests in `tests/test_smoke.py`; no automated app coverage | The frozen test list has no app module, but strict TDD applies to the Streamlit slice and `tests/test_smoke.py` belongs to another member's slice, so it cannot hold app tests without breaking parallel ownership. `tests/test_app.py` is the smallest addition that keeps ownership disjoint and the helpers covered. Flagged as an open question for the orchestrator. |

## Data Flow

    SCENARIOS (scenarios.py)
        │
        └──▶ run_scenarios ──▶ [ScenarioRun] ──┬──▶ charts.plot_queue_evolution (per run)
                                               │    charts.plot_wait_times      (per run)
                                               │
                                               └──▶ analysis.summarize ──▶ [ScenarioSummary]
                                                                              │
                       theory: theoretical_metrics ◀── oracle ────────────────┤
                                                                              ├──▶ tables.comparison_dataframe ──▶ CSV + LaTeX
                                                                              └──▶ charts.plot_theory_vs_sim
                                                                                   charts.plot_scenario_comparison

    python -m mm1 (cli.py) ──wires all of the above──▶ outputs/  (exit code 0)
    app/streamlit_app.py   ──sliders(lam, mu)──▶ run_mm1 + theoretical_metrics
                           ──▶ live table + queue animation + interactive charts

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/mm1/__init__.py` | Create | Re-export the public API of the six modules |
| `src/mm1/__main__.py` | Create | Minimal shim so `python -m mm1` reaches `cli.main` (decision D11) |
| `src/mm1/metrics.py` | Create | `TheoryMetrics`, `utilization`, `is_stable`, `theoretical_metrics` |
| `src/mm1/simulation.py` | Create | `CustomerRecord`, `ScenarioRun`, `run_mm1` (SimPy engine) |
| `src/mm1/scenarios.py` | Create | `Scenario`, `SCENARIOS`, `run_scenarios` |
| `src/mm1/analysis.py` | Create | `ScenarioSummary`, `confidence_interval`, `relative_error`, `summarize` |
| `src/mm1/tables.py` | Create | `comparison_dataframe`, `write_csv`, `to_latex` |
| `src/mm1/charts.py` | Create | Four plot functions plus `generate_all` |
| `src/mm1/cli.py` | Create | `main` entry point with `--lam/--mu/--scenarios/--replications/--sim-time/--seed/--warmup/--out` |
| `app/streamlit_app.py` | Create | Streamlit resource (sliders, guard, animation, live table, charts) |
| `tests/test_*.py` | Create | One pytest module per source module, plus `tests/test_app.py` for the app helpers (decision D12) |
| `reports/figures/**` | Create | Figures used by the document (owner: Cael Soto) |
| `reports/ape3_mm1.tex`, `reports/ape3_mm1.pdf`, `reports/README.md`, `reports/assets/**` | Create | Technical document, demo video link, defense notes (owner: Domenica Rojas) |
| `docs/division-trabajo.md` | Create | Spanish work division (this planning change) |
| `outputs/**` | Generated | CSV/PNG; gitignored and regenerable |

## Interfaces / Contracts

Frozen public signatures — no deviations; internal helpers are free.

```python
# src/mm1/metrics.py
@dataclass(frozen=True)
class TheoryMetrics:
    rho: float; L: float; Lq: float; W: float; Wq: float

def utilization(lam: float, mu: float) -> float
def is_stable(lam: float, mu: float) -> bool
def theoretical_metrics(lam: float, mu: float) -> TheoryMetrics

# src/mm1/simulation.py
@dataclass(frozen=True)
class CustomerRecord:
    customer_id: int; arrival_time: float; service_start: float
    departure_time: float; wait_time: float; service_time: float

@dataclass(frozen=True)
class ScenarioRun:
    scenario: int; lam: float; mu: float; seed: int
    sim_time: float; warmup: float; n_customers: int
    mean_wait: float; mean_queue: float; mean_system_time: float
    mean_in_system: float; utilization: float
    customers: tuple[CustomerRecord, ...]
    queue_trace: tuple[tuple[float, int], ...]

def run_mm1(lam: float, mu: float, sim_time: float = 1000.0,
            seed: int | None = None, scenario: int = 0,
            warmup: float = 0.0) -> ScenarioRun

# src/mm1/scenarios.py
@dataclass(frozen=True)
class Scenario:
    id: int; lam: float; mu: float; label: str; condition: str

SCENARIOS: tuple[Scenario, ...]   # the 3 guide scenarios, ids 1..3
def run_scenarios(replications: int = 30, sim_time: float = 1000.0,
                  base_seed: int = 42, warmup: float = 0.0) -> list[ScenarioRun]

# src/mm1/analysis.py
@dataclass(frozen=True)
class ScenarioSummary:
    scenario: int; lam: float; mu: float; replications: int
    theory: TheoryMetrics
    sim_mean_wait: float; sim_mean_queue: float
    sim_mean_in_system: float; sim_utilization: float
    std_wait: float; ci95_wait: tuple[float, float]
    rel_error_L: float; rel_error_Lq: float
    rel_error_W: float; rel_error_Wq: float

def confidence_interval(values: Sequence[float], confidence: float = 0.95) -> tuple[float, float]
def relative_error(simulated: float, theoretical: float) -> float
def summarize(runs: Sequence[ScenarioRun]) -> list[ScenarioSummary]

# src/mm1/tables.py
def comparison_dataframe(summaries: Sequence[ScenarioSummary]) -> "pandas.DataFrame"
def write_csv(df: "pandas.DataFrame", path: str | Path) -> Path
def to_latex(df: "pandas.DataFrame", path: str | Path) -> Path

# src/mm1/charts.py
def plot_queue_evolution(run: ScenarioRun, path: str | Path) -> Path
def plot_wait_times(run: ScenarioRun, path: str | Path) -> Path
def plot_theory_vs_sim(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path
def plot_scenario_comparison(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path
def generate_all(runs: Sequence[ScenarioRun], summaries: Sequence[ScenarioSummary],
                 out_dir: str | Path) -> list[Path]

# src/mm1/cli.py
def main(argv: Sequence[str] | None = None) -> int   # entry point: python -m mm1
```

Additive app contract (internal to `app/`, not part of the package API):

```python
# app/streamlit_app.py
def theory_row(lam: float, mu: float) -> dict[str, float]
def stability_message(lam: float, mu: float) -> str
def scenario_table(summaries: Sequence[ScenarioSummary]) -> "pandas.DataFrame"
def build_queue_figure(run: ScenarioRun) -> "matplotlib.figure.Figure"
def build_comparison_figure(summaries: Sequence[ScenarioSummary]) -> "matplotlib.figure.Figure"
```

### Ownership map (disjoint file sets)

| Member | Files | Spec ids |
|--------|-------|----------|
| Jaime Landazuri | `src/mm1/simulation.py`, `src/mm1/cli.py`, `tests/test_simulation.py`, `tests/test_smoke.py` | S4, S7, S12, S13 |
| Richard Chamba | `src/mm1/metrics.py`, `src/mm1/scenarios.py`, `src/mm1/analysis.py`, `tests/test_metrics.py`, `tests/test_scenarios.py`, `tests/test_analysis.py` | S3, S5, S6 |
| Cael Soto | `src/mm1/tables.py`, `src/mm1/charts.py`, `tests/test_tables.py`, `tests/test_charts.py`, `reports/figures/**` | S6, S7 |
| Domenica Rojas | `app/streamlit_app.py`, `tests/test_app.py`, `reports/ape3_mm1.tex`, `reports/ape3_mm1.pdf`, `reports/README.md`, `reports/assets/**` | S8, S9, S11, S15 |
| Orchestrator (foundation) | `src/mm1/__init__.py`, `src/mm1/__main__.py`, `requirements.txt`, `pyproject.toml`, `.gitignore`, `README.md` | S2, S10, S12 |

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Theory formulas and boundary (`lam == mu`), scenario table, FIFO ordering, single-server serialization, seed determinism, warmup exclusion, CI and relative error, table columns, app pure helpers | pytest with hand-computed analytic values for all three scenarios (`L`, `Lq`, `W`, `Wq`) and `1e-9` tolerances |
| Integration | `run_scenarios` → `summarize` → `comparison_dataframe` → `write_csv`/`to_latex` on a `tmp_path` with `sim_time=100`, `replications=3` | One integration test in `tests/test_analysis.py`; CLI wiring asserted through `cli.main([...])` with `tmp_path` output |
| E2E | None | No browser runner is planned; the Streamlit app is covered through its pure helpers (design decision D10) |
| Structural | Figures exist, are non-empty, PNG signature, `Agg` backend forced | File-level assertions only; never pixel comparisons |

TDD order per module: RED test module → GREEN implementation → PRESERVE one test
for each pre-existing behavior the change touches → REFACTOR with green tests.

## Threat Matrix

N/A — this change adds no routing, shell command execution, subprocess,
VCS/PR automation, executable-file classification, or process-integration
boundary. `python -m mm1` is an in-process Python entry point driven by
`argparse`, not a shell wrapper, and the Streamlit app is a local UI.

| Boundary | Applicability | Reason |
|---|---|---|
| Documentation-like paths | N/A | No file is classified or executed by extension; nothing runs `.txt`/`.md` as code |
| Git repository selection | N/A | Planning work runs no git commands; delivery is done by the orchestrator |
| Commit state | N/A | No staging or commit automation exists in the project |
| Push state | N/A | No push automation exists in the project |
| PR commands | N/A | PRs are created manually by the team; no `gh` automation in scope |

## Migration / Rollout

No migration required. `outputs/` is gitignored and regenerated by
`python -m mm1 --out outputs`; `openspec/specs/` stays empty until `sdd-archive`
merges the deltas. Rollout is per member slice, one stacked PR at a time to
`main`, so an unmerged slice leaves `main` working.

## Open Questions

All four questions below were resolved by the orchestrator (Jaime Landazuri) on
2026-10-15 before the foundation PR; the resolutions are binding for `sdd-apply`.

- [x] D11 APPROVED: `src/mm1/__main__.py` (3-line shim) is added to the frozen map
      and an editable install (`pip install -e .`) is the documented CLI prerequisite.
      Landed with the foundation slice; the public contract is unchanged because
      dispatch still lives in `cli.main`.
- [x] D12 APPROVED: `tests/test_app.py` is added so the Streamlit slice keeps strict
      TDD without crossing member file ownership. Owned by Domenica Rojas.
- [x] RESOLVED — report output format: LaTeX authored in Overleaf, submitted as PDF
      (`reports/ape3_mm1.tex` + `reports/ape3_mm1.pdf`). Rationale: the same team
      already submits this course with Overleaf (`simulacion_repo` APE 002), guide §8
      grades structure/presentation only, and a `.tex` source keeps the figures and
      tables reproducible from `outputs/`. A Word export is a fallback, not a second
      source of truth.
- [x] RESOLVED — demo video hosting: an unlisted YouTube link recorded in
      `reports/README.md`, with a short backup clip kept out of git because of size.
      Rationale: guide §8 requires a demonstration video and the classroom has no
      guaranteed network for a repository-hosted asset.
