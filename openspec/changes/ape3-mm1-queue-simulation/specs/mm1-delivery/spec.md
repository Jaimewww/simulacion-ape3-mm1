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

### Requirement: The interface MUST be command line only

The practice MUST have **no interactive interface**: no web UI, no `app/` directory, no
form, no slider and no server. The demonstration MUST run from the command line, which is
what guide §5 asks for: Python + SimPy + NumPy + Matplotlib. `requirements.txt` and
`pyproject.toml` MUST NOT declare any web framework. Specs: S19.

#### Scenario: No interactive interface exists

- GIVEN the delivered source tree
- WHEN `grep -ri streamlit src tests app pyproject.toml requirements.txt` is run
- THEN it returns nothing
- AND no `app/` directory exists

#### Scenario: The package imports no web framework

- GIVEN a checkout with no web framework installed
- WHEN `python -c "import mm1, sys; assert not any(m in sys.modules for m in ('streamlit', 'gradio', 'dash'))"` runs
- THEN it exits 0

### Requirement: The queue animation MUST be renderable headlessly

`view/animation.py` MUST render the queue evolution of one run to an animated file using
`matplotlib.animation`, forcing the `Agg` backend before importing pyplot, so it needs no
display. `render_queue_animation(run, out_dir, fps=20, max_frames=200)` MUST write both
`cola.mp4` and `cola.gif` into `out_dir` and return their paths. The pure helpers
`frame_frames(trace, sim_time, max_frames)` and `queue_animation_figure(run, frames)`
MUST be importable and testable without running the encoder, so the test suite never
depends on ffmpeg being present. Specs: S19, S20.

#### Scenario: Both animation files are produced

- GIVEN a completed stable run and a temporary directory
- WHEN `render_queue_animation(run, tmp_path)` is called
- THEN `cola.mp4` and `cola.gif` both exist and are non-empty
- AND no display was opened

#### Scenario: Frame sampling is bounded and monotonic

- GIVEN a `queue_trace` of 500 entries and `max_frames = 50`
- WHEN `frame_frames(trace, sim_time, 50)` is called
- THEN at most 50 sub-traces are returned
- AND each starts at the first trace entry
- AND the last one covers the whole trace
- AND `max_frames = 0` raises `ValueError`

#### Scenario: The command line exposes the animation

- GIVEN `python -m mm1 --lam 2.0 --mu 3.0 --sim-time 200 --animate --out DIR`
- WHEN the command finishes
- THEN it exits 0 and `DIR` contains `cola.mp4` and `cola.gif`
- AND a run without `--animate` does not import the animation module

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
them. `import mm1` MUST NOT import any web framework or the animation stack, and the
command line MUST stay the only entry point. Specs: S16, S19.

#### Scenario: The model never depends on a presentation layer

- GIVEN `src/mm1/model/`
- WHEN every module in it is inspected for imports
- THEN no module imports `mm1.view` or `mm1.controller`

#### Scenario: The package import stays dependency-free

- GIVEN a checkout in which no web framework is installed
- WHEN `python -c "import mm1, sys; assert 'streamlit' not in sys.modules"` runs
- THEN it exits 0

#### Scenario: Every entry point shares one service

- GIVEN the exported tables, the figures and the animation
- WHEN any of them needs study results
- THEN it goes through `mm1.controller.run_study`, so the document, the exported table
  and the animation cannot report different numbers

### Requirement: The contribution order MUST be documented

`CONTRIBUTING.md` MUST contain an ordered contribution table whose rows sequence the
contributions from the shared foundation to the final deliverable, MUST
name the responsible member in every row, and MUST place the document and the
demonstration video as the final rows (S17, S18, S20). Its order MUST match the phase
order in `tasks.md`. Specs: S17, S18, S20.

#### Scenario: The final rows are the document and the video

- GIVEN `CONTRIBUTING.md`
- WHEN the main contribution table is read from top to bottom
- THEN the last technical row is Domenica Rojas's queue animation and every row
  names one of the four members
- AND the closing table ends with the technical document and the demonstration video

#### Scenario: The order matches the task plan

- GIVEN `CONTRIBUTING.md` and `tasks.md`
- THEN the stage order in the document matches the phase order in the plan
