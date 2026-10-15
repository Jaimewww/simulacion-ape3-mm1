# Delta for mm1-delivery

## ADDED Requirements

### Requirement: The CLI MUST run the practice end to end

`python -m mm1` (backed by `src/mm1/controller/cli.py::main(argv) -> int`) MUST run the three
guide scenarios, write the comparison table and the figures, and return exit code
`0`. It MUST accept `--scenarios`, `--replications`, `--sim-time`, `--seed`,
`--warmup`, `--out`, and the single-run options `--lam` and `--mu`. For unstable
input (`lam >= mu`) it MUST print exactly `El sistema no es estable` and return a
non-zero exit code without writing files. Specs: S4, S6, S7.

#### Scenario: Default run produces the deliverables

- GIVEN the package is installed and the working directory is writable
- WHEN `python -m mm1 --out outputs` is executed
- THEN the exit code is `0`
- AND `outputs/` contains the comparison CSV, the LaTeX table, and the figures
- AND the CSV has one row per guide scenario

#### Scenario: Unstable single run is refused

- GIVEN `--lam 3.0 --mu 3.0`
- WHEN `main(["--lam", "3.0", "--mu", "3.0"])` is called
- THEN stdout contains `El sistema no es estable`
- AND the returned exit code is non-zero
- AND no CSV, LaTeX or PNG file is created

#### Scenario: Replication count is honored

- GIVEN `--replications 5 --sim-time 200 --seed 42`
- WHEN the command runs
- THEN the exit code is `0`
- AND the summary uses 5 replications per scenario

### Requirement: The interactive resource MUST be a Streamlit app

`app/streamlit_app.py` MUST provide sliders for `lambda` and `mu`, display `rho`
with a stability guard, offer a run button, show the queue evolution as an
animation, show a live theory-vs-simulation table, and render at least two
interactive charts over the three guide scenarios. Pure helpers `theory_row(lam,
mu)`, `stability_message(lam, mu)`, `scenario_table(summaries)`,
`build_queue_figure(run)` and `build_comparison_figure(summaries)` MUST be
importable without launching Streamlit so they can be unit tested. Specs: S11, S15.

#### Scenario: Stability guard message

- GIVEN `stability_message(3.0, 3.0)` and `stability_message(2.0, 3.0)`
- THEN the first returns an unstable/blocked message and the second a stable one

#### Scenario: Theory row is derived from theory functions

- GIVEN `theory_row(2.0, 3.0)`
- THEN the returned mapping contains `rho`, `L`, `Lq`, `W` and `Wq`
- AND the values equal `theoretical_metrics(2.0, 3.0)`

#### Scenario: App is served from the repository root

- GIVEN the repository root
- WHEN `streamlit run app/streamlit_app.py` is launched
- THEN the app starts without importing `src/mm1` from an absolute path

### Requirement: The technical document MUST cover the graded criteria

`reports/` MUST contain the technical document covering structure and
presentation, procedure, results and evidence (theory vs simulation tables and
figures for the three scenarios), the 10 control questions of guide §7 answered,
conclusions tied to the practice objectives, and a link to the demonstration
video. `docs/division-trabajo.md` MUST assign files, spec ids, deliverables,
acceptance checks, branch name and PR policy to each of the four members, plus an
"how to work with AI agents" section. Specs: S8, S9, S10.

#### Scenario: Control questions are all answered

- GIVEN the technical document
- THEN it lists 10 numbered answers matching guide §7
- AND it includes the verbatim questions `¿Por qué SimPy utiliza una distribución
  exponencial para generar los tiempos?`, `¿Por qué los resultados simulados pueden
  ser diferentes de los resultados teóricos?` and `¿Qué ocurriría si λ fuera mayor
  que μ??`
- AND every answer references the simulated evidence used

#### Scenario: Conclusions are tied to the objectives

- GIVEN the technical document
- THEN the conclusions section maps to the three practice objectives and to the
  expected behavior stated in guide §6 (wait time and queue grow as `lambda`
  approaches `mu`)

#### Scenario: Work division is complete for four members

- GIVEN `docs/division-trabajo.md`
- THEN each of the four members has owned files, spec ids, deliverables, an
  acceptance check, a `feat/<member>-<topic>` branch and a PR-to-`main` policy

### Requirement: Reproducibility and delivery constraints

The repository MUST be public, MUST be Python-based, and MUST let one command
regenerate every reported artifact. This planning change MUST NOT execute
`sdd-apply`. Specs: S12, S13, S14, S15.

#### Scenario: Artifacts are regenerable

- GIVEN a clean checkout with dependencies installed
- WHEN `python -m mm1 --out outputs` runs followed by `python -m pytest -q`
- THEN both commands succeed and every figure and table referenced by the
  document is produced by that command

#### Scenario: Planning scope is respected

- GIVEN the change folder
- THEN it contains only planning artifacts (`state.yaml`, `proposal.md`, specs,
  `design.md`, `tasks.md`) and no source or test files

### Requirement: The package MUST be structured as MVC

`src/mm1` MUST be split into `model/`, `view/` and `controller/` (S16). Modules in
`model/` MUST NOT import `mm1.view` or `mm1.controller`. Modules in `view/` MUST NOT
compute domain results and MUST go through `mm1.controller.run_study` when they need
them. `import mm1` MUST NOT import Streamlit, and `app/streamlit_app.py` MUST stay a
thin entry point so `streamlit run app/streamlit_app.py` remains the documented
command. Specs: S16.

#### Scenario: The model never depends on a presentation layer

- GIVEN `src/mm1/model/`
- WHEN every module in it is inspected for imports
- THEN no module imports `mm1.view` or `mm1.controller`

#### Scenario: The package import stays dependency-free

- GIVEN a checkout in which Streamlit is not installed
- WHEN `python -c "import mm1, sys; assert 'streamlit' not in sys.modules"` runs
- THEN it exits 0

#### Scenario: Both front ends share one service

- GIVEN the interactive page and the command line
- WHEN either one needs the study results
- THEN it calls `mm1.controller.run_study`, so the document and the live resource
  cannot report different numbers

### Requirement: The contribution order MUST be documented

`CONTRIBUTING.md` MUST contain an ordered contribution table whose rows sequence the
contributions from the shared foundation to the interactive Streamlit resource, MUST
name the responsible member in every row, and MUST place the visual resource as the
final technical deliverable (S17, S18). Its order MUST match the phase order in
`tasks.md`. Specs: S17, S18.

#### Scenario: The visual resource is the final row

- GIVEN `CONTRIBUTING.md`
- WHEN the main contribution table is read from top to bottom
- THEN the last row is Domenica Rojas's Streamlit interactive resource and every row
  names one of the four members

#### Scenario: The order matches the task plan

- GIVEN `CONTRIBUTING.md` and `tasks.md`
- THEN the stage order in the document matches the phase order in the plan
