# Design: APE 003 — M/M/1 queue simulation with SimPy

## Technical Approach

One Python package, `src/mm1`, built theory-first and structured as MVC (S16):

| Layer | Package | Contents | Dependency rule |
|-------|---------|----------|-----------------|
| Model | `src/mm1/model/` | `metrics.py` (guide §5.1 formulas — the correctness oracle), `simulation.py` (SimPy FIFO single-server engine, immutable records, queue trace), `scenarios.py` (the three guide scenarios as data + replicas), `analysis.py` (aggregation, CI95, relative error) | No rendering, no I/O. MUST NOT import `mm1.view` or `mm1.controller`. |
| View | `src/mm1/view/` | `tables.py` (comparison table → DataFrame/CSV/LaTeX), `charts.py` (Matplotlib figures), `animation.py` (headless queue animation) | Renders only; MUST NOT compute domain results. Imports `mm1.model`, and when it needs results it asks `mm1.controller` instead of computing them. |
| Controller | `src/mm1/controller/` | `study.py` (the `run_study` application service), `cli.py` (`python -m mm1`) | The only layer allowed to know more than one layer; it drives the model and triggers the views. |

`controller/study.py` exists so every entry point calls **one** service: the figures in
the document, the animation and the exported tables cannot diverge. The only entry
point is the command line (`python -m mm1`); there is no web interface (decision D16).

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
| D7 | ~~Streamlit for the interactive resource~~ — **supereded by D16** | Jupyter notebook (`ipywidgets`); Plotly Dash | Originally chosen because the teacher approved an interactive graphic resource (S15). The teacher later required no interactive interface (S19), so this decision is void. |
| D8 | `python -m mm1` as the single orchestration entry point | Scripts per stage; Makefile | The demo video and the report need one reproducible command; CLI flags cover the manual single-`lam`/`mu` probe. |
| D9 | Four disjoint member slices, one PR each | One shared branch per feature area | S14 needs four AI agents working in parallel with no merge conflicts; each slice owns whole files. |
| D10 | ~~App helpers as importable pure functions tested without Streamlit~~ — **superseded by D16**; the same principle now applies to the animation helpers | Streamlit AppTest E2E only | The original reasoning still holds for what replaced the app: the animation module exposes pure helpers so it can be unit-tested without a display. |
| D11 | Add `src/mm1/__main__.py` as a 3-line shim (`from mm1.controller.cli import main; raise SystemExit(main())`), and require an editable install | Declare a `mm1` console script in `pyproject.toml`; drop `python -m mm1`; put the dispatch inside `__init__.py` | The frozen map lists only `__init__.py` and `cli.py`, but `python -m mm1` (frozen entry point) is only executable through `mm1/__main__.py`, and `src/` is only importable outside pytest after `pip install -e .` (observed: `.venv/bin/python -m mm1 --help` fails with `No module named mm1` in the current skeleton, which has neither). This is the smallest addition that keeps the frozen entry point working; the dispatch logic still lives in `cli.main`, so the public contract is unchanged. Flagged as an open question for the orchestrator. |
| D12 | `tests/test_animation.py` covers the animation renderer | Put its tests in `tests/test_smoke.py`; no automated coverage of the animation | The frozen test list has no module for it, but strict TDD applies to the animation slice and `tests/test_smoke.py` belongs to another member's slice, so it cannot hold those tests without breaking parallel ownership. `tests/test_animation.py` is the smallest addition that keeps ownership disjoint and the renderer covered. (Was `tests/test_app.py` for the cancelled Streamlit helpers.) |
| D13 | Structure the package as MVC: `model/`, `view/`, `controller/` (S16) | Flat `src/mm1/*.py`; layered but unnamed; MVVM | The user asked for MVC by name (S16). Naming the layers makes the dependency direction checkable (`model` never imports `view`) and gives every member one unambiguous layer. The command line is simultaneously the input surface and the composition root, so `cli.py` lives in `controller/` and calls the shared `run_study` service; views never compute. |
| D14 | `StudyResult(runs, summaries)` carries model data only | Return a `pandas.DataFrame`; return a rendered dict | Keeps the controller free of any view or third-party dependency, so `mm1.view.tables` stays the only place that builds a DataFrame and the MVC dependency rule is mechanically true. |
| D15 | `confidence_interval` is the two-sided **Student-t interval of the mean**, `mean ± t((1+confidence)/2, n-1)·s/√n`, implemented with the standard library only | `mean ± s`; normal (z) quantile; one-sided interval; bootstrap | The plan's original example (`[1,2,3] → (1,3)`) was `mean ± s`, which contradicts the t requirement stated in the same spec — a real contradiction found while implementing stage 5. The t interval is what makes "theory inside the 95 % interval" a defensible claim in the report (already the measured evidence for S6 below). SciPy is not in `requirements.txt` and guide §3 lists only NumPy and Matplotlib, so the quantile is a standard-library implementation pinned against the `t(0.975, df)` oracle in task 4.3. |
| D16 | The interactive Streamlit resource is **cancelled** (teacher: "la práctica no debe tener interfaz interactiva", decision S19); the demonstration returns to the command line | Keep Streamlit anyway; replace it with a local HTML/Plotly page; drop the visual demonstration entirely | Guide §5 asks for charts from Python, not a web GUI. The CLI already runs the three scenarios and exports the table and figures, so the terminal is the correct demo surface. The only visual element the app had that the CLI lacks is the queue animation, which is kept as a headless `matplotlib.animation` render (mp4 + gif verified without a display). This also removes Streamlit from the runtime, so `import mm1` pulls in no web framework. |
| D17 | The queue animation lives in `view/animation.py` as a pure renderer, and the CLI gets an `--animate` flag that calls it | Put the animation inside `controller/cli.py`; add a separate `python -m mm1.animate` module; keep it only in the video, not in code | The animation is a view concern, but the user asked to expose it through the CLI. Splitting it keeps the surfaces disjoint: `controller/cli.py` (Jaime) owns the flag and the wiring, `view/animation.py` (Domenica) owns the renderer and its tests, so neither edits the other's file. `charts.py` keeps producing the static per-replica queue figures it already writes; the animation is a separate, additional artifact. |

## Data Flow

    model/scenarios.SCENARIOS
        │
        └──▶ model.run_scenarios ──▶ [ScenarioRun] ──┬──▶ view.charts.plot_queue_evolution (per run)
                                                     │    view.charts.plot_wait_times      (per run)
                                                     │
                                                     └──▶ model.summarize ──▶ [ScenarioSummary]
                                                                                   │
                     model.theoretical_metrics ◀── oracle ────────────────────────┤
                                                                                   ├──▶ view.tables.comparison_dataframe ──▶ CSV + LaTeX
                                                                                   └──▶ view.charts.plot_theory_vs_sim
                                                                                        view.charts.plot_scenario_comparison

    controller/study.run_study ──▶ StudyResult(runs, summaries)   ← the one shared service
            ▲
            │
    controller/cli.main (python -m mm1)
            ├──▶ run_study + view.tables/charts ──▶ outputs/         (table + figures)
            └──▶ [--animate] view.animation.render_queue_animation ──▶ cola.mp4 + cola.gif

    The command line is the ONLY entry point (decision D16); there is no web page.

Dependency direction, mechanically checkable: `model` imports no other layer;
`view` imports `model` only; `controller` imports `model` and triggers `view`. No cycle.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/mm1/__init__.py` | Create | Re-export the public API of the three layers (25 names) |
| `src/mm1/model/__init__.py` | Create | Model layer facade (the `M`) |
| `src/mm1/view/__init__.py` | Create | View layer facade (the `V`); excludes `animation.py` so `import mm1` stays free of the animation stack |
| `src/mm1/controller/__init__.py` | Create | Controller layer facade (the `C`) |
| `src/mm1/__main__.py` | Create | Minimal shim so `python -m mm1` reaches `cli.main` (decision D11) |
| `src/mm1/model/metrics.py` | Create | `TheoryMetrics`, `utilization`, `is_stable`, `theoretical_metrics` |
| `src/mm1/model/simulation.py` | Create | `CustomerRecord`, `ScenarioRun`, `run_mm1` (SimPy engine) |
| `src/mm1/model/scenarios.py` | Create | `Scenario`, `SCENARIOS`, `run_scenarios` |
| `src/mm1/model/analysis.py` | Create | `ScenarioSummary`, `confidence_interval`, `relative_error`, `summarize` |
| `src/mm1/view/tables.py` | Create | `comparison_dataframe`, `write_csv`, `to_latex` |
| `src/mm1/view/charts.py` | Create | Four plot functions plus `generate_all` |
| `src/mm1/controller/cli.py` | Create | `main` entry point with `--lam/--mu/--scenarios/--replications/--sim-time/--seed/--warmup/--out/--animate` |
| `src/mm1/controller/study.py` | Create | `StudyResult`, `run_study` — the service every entry point shares (D13, D14) |
| `src/mm1/view/animation.py` | Create | `render_queue_animation(run, out_dir, fps, max_frames)` plus its pure helpers — the headless queue animation (D16, D17) |
| `tests/test_*.py` | Create | One pytest module per source module, plus `tests/test_animation.py` for the animation renderer (decision D12) |
| `reports/figures/**` | Create | Figures used by the document (owner: Cael Soto) |
| `reports/ape3_mm1.tex`, `reports/ape3_mm1.pdf`, `reports/README.md`, `reports/assets/**` | Create | Technical document, demo video link, defense notes (owner: Domenica Rojas) |
| `docs/division-trabajo.md` | Create | Spanish work division (this planning change) |
| `outputs/**` | Generated | CSV/PNG; gitignored and regenerable |

## Interfaces / Contracts

Frozen public signatures — no deviations; internal helpers are free.

```python
# src/mm1/model/metrics.py
@dataclass(frozen=True)
class TheoryMetrics:
    rho: float; L: float; Lq: float; W: float; Wq: float

def utilization(lam: float, mu: float) -> float
def is_stable(lam: float, mu: float) -> bool
def theoretical_metrics(lam: float, mu: float) -> TheoryMetrics

# src/mm1/model/simulation.py
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

# src/mm1/model/scenarios.py
@dataclass(frozen=True)
class Scenario:
    id: int; lam: float; mu: float; label: str; condition: str

SCENARIOS: tuple[Scenario, ...]   # the 3 guide scenarios, ids 1..3
def run_scenarios(replications: int = 30, sim_time: float = 1000.0,
                  base_seed: int = 42, warmup: float = 0.0) -> list[ScenarioRun]

# src/mm1/model/analysis.py
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

# src/mm1/view/tables.py
def comparison_dataframe(summaries: Sequence[ScenarioSummary]) -> "pandas.DataFrame"
def write_csv(df: "pandas.DataFrame", path: str | Path) -> Path
def to_latex(df: "pandas.DataFrame", path: str | Path) -> Path

# src/mm1/view/charts.py
def plot_queue_evolution(run: ScenarioRun, path: str | Path) -> Path
def plot_wait_times(run: ScenarioRun, path: str | Path) -> Path
def plot_theory_vs_sim(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path
def plot_scenario_comparison(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path
def generate_all(runs: Sequence[ScenarioRun], summaries: Sequence[ScenarioSummary],
                 out_dir: str | Path) -> list[Path]

# src/mm1/controller/study.py
@dataclass(frozen=True)
class StudyResult:
    runs: tuple[ScenarioRun, ...]; summaries: tuple[ScenarioSummary, ...]

def run_study(replications: int = 30, sim_time: float = 1000.0,
              base_seed: int = 42, warmup: float = 0.0) -> StudyResult

# src/mm1/controller/cli.py
def main(argv: Sequence[str] | None = None) -> int   # entry point: python -m mm1
```

View contract (internal to `src/mm1/view/`, not part of the package API: importing the
animation stack is expensive, and `import mm1` MUST stay dependency-free). The command
line calls it when `--animate` is given.

```python
# src/mm1/view/animation.py
def render_queue_animation(run: ScenarioRun, out_dir: str | Path,
                           fps: int = 20, max_frames: int = 200) -> list[Path]
def frame_frames(trace: Sequence[tuple[float, int]], sim_time: float,
                 max_frames: int) -> list[list[tuple[float, int]]]
def queue_animation_figure(run: ScenarioRun, frames: int) -> tuple[Figure, Callable[[int], tuple]]
```

`render_queue_animation` MUST write both `cola.mp4` and `cola.gif` into `out_dir` and
return their paths, MUST force the `Agg` backend before importing pyplot, and MUST NOT
require a display. The pure helpers (frame sampling and figure construction) MUST be
testable without running the encoder, so the test suite never depends on ffmpeg.

### Ownership map (disjoint file sets)

| Member | Files | Spec ids |
|--------|-------|----------|
| Jaime Landazuri | `src/mm1/model/simulation.py`, `src/mm1/controller/cli.py`, `tests/test_simulation.py`, `tests/test_smoke.py` | S4, S7, S12, S13 |
| Richard Chamba | `src/mm1/model/metrics.py`, `src/mm1/model/scenarios.py`, `src/mm1/model/analysis.py`, `src/mm1/controller/study.py`, `tests/test_metrics.py`, `tests/test_scenarios.py`, `tests/test_analysis.py` | S3, S5, S6, S16 |
| Cael Soto | `src/mm1/view/tables.py`, `src/mm1/view/charts.py`, `tests/test_tables.py`, `tests/test_charts.py`, `reports/figures/**` | S6, S7 |
| Domenica Rojas | `src/mm1/view/animation.py`, `tests/test_animation.py`, `reports/ape3_mm1.tex`, `reports/ape3_mm1.pdf`, `reports/README.md`, `reports/assets/**` | S8, S9, S19, S20 |
| Orchestrator (foundation) | `src/mm1/__init__.py`, `src/mm1/__main__.py`, `src/mm1/model/__init__.py`, `src/mm1/view/__init__.py`, `src/mm1/controller/__init__.py`, `requirements.txt`, `pyproject.toml`, `.gitignore`, `README.md`, `CONTRIBUTING.md` | S2, S10, S12, S16, S17 |

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Theory formulas and boundary (`lam == mu`), scenario table, FIFO ordering, single-server serialization, seed determinism, warmup exclusion, CI and relative error, table columns, animation pure helpers | pytest with hand-computed analytic values for all three scenarios (`L`, `Lq`, `W`, `Wq`) and `1e-9` tolerances |
| Integration | `run_scenarios` → `summarize` → `comparison_dataframe` → `write_csv`/`to_latex` on a `tmp_path` with `sim_time=100`, `replications=3`; and one command regenerating every reported artifact | One integration test in `tests/test_analysis.py`; CLI wiring asserted through `cli.main([...])` with `tmp_path` output, including the exported CSV, LaTeX and figure files |
| E2E | None | No browser runner is planned. The animation renderer is covered through its pure helpers plus its actual output files (decision D12) |
| Structural | Figures exist, are non-empty, PNG signature, `Agg` backend forced; the animation writes a non-empty mp4 and gif | File-level assertions only; never pixel comparisons. The frame-sampling helper is unit-tested so the suite does not depend on ffmpeg |

TDD order per module: RED test module → GREEN implementation → PRESERVE one test
for each pre-existing behavior the change touches → REFACTOR with green tests.

### Measured evidence for the reporting slices (stage 3, PR 3)

Running the engine against `theoretical_metrics` on 2026-10-15 with
`sim_time=2000` produced the numbers the document must use to answer guide §7
question 9 ("why can the simulated results differ from the theoretical ones?"):

| Scenario | Single run vs theory (`Wq`, `Lq`) | Mean of 12 replicas vs theory | Theory inside the 30-replica CI95? |
|----------|-----------------------------------|-------------------------------|-------------------------------------|
| `2.0, 3.0` | +5.7 %, +5.0 % | +1.9 % | yes |
| `2.5, 3.0` | +0.3 %, +2.1 % | +1.5 % | yes |
| `2.9, 3.0` | +74 %, +76 % | +7.4 % | yes |

The error falls as the horizon grows (`lambda = 2.0`: 12.9 % at `sim_time=500`,
5.7 % at 2000, 2.5 % at 10000, 1.6 % at 50000), so the engine is consistent, not
biased. At `rho = 0.967` the waiting time has a heavy tail, so **a single run is
not evidence**; the mean over replicas is, and the theory lands inside the 95 %
interval for all three scenarios. This is the measured justification for the 30
default replications and for `analysis` reporting CI95 and relative error.
Little's law holds on the simulated outputs to within 0.9 %.

## Threat Matrix

N/A — this change adds no routing, shell command execution, subprocess,
VCS/PR automation, executable-file classification, or process-integration
boundary. `python -m mm1` is an in-process Python entry point driven by
`argparse`, not a shell wrapper. The animation calls the ffmpeg binary through
`matplotlib.animation`, with a fixed argument vector built from the output path —
no user-supplied path reaches a shell.

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
- [x] D12 APPROVED: `tests/test_animation.py` is added so the animation slice keeps
      strict TDD without crossing member file ownership. Owned by Domenica Rojas.
      (Originally `tests/test_app.py` for the cancelled Streamlit helpers.)
- [x] RESOLVED 2026-10-15 — the teacher required no interactive interface (S19). The
      Streamlit resource is cancelled (D16) and the stage-10 work is re-planned onto
      the command line (D17): `--animate` generates the queue animation headless. No
      web framework remains in the runtime.
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
