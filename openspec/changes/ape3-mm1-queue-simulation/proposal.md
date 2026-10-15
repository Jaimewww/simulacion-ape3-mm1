# Proposal: APE 003 — M/M/1 queue simulation with SimPy

## Intent

The Simulación course practice APE 003 requires a working M/M/1 waiting-line
simulation in Python + SimPy, an interactive graphic resource, a technical
document and an oral defense. The four-member team also asked for a plan its
members can execute with AI coding agents independently. This change delivers
the sanctioned plan only: the `openspec/` artifacts plus the work-division
document that turn the signed guide (§1–§10) into executable, testable tasks.

Traceability: S1–S15 of `odd/tasks/ape3-mm1-queue-simulation.md`.

## Scope

### In Scope

- `openspec/` planning artifacts (init config, proposal, specs, design, tasks).
- A frozen module map, public interface contract and per-member file ownership.
- `docs/division-trabajo.md` (Spanish) with per-member files, spec ids,
  deliverables, acceptance checks, branch/PR policy and AI-agent instructions.
- `.atl/skill-registry.md` so delegated agents receive exact skill paths.

### Out of Scope

- Source code, tests, `README.md`, `requirements.txt`, `pyproject.toml`
  (owned by a parallel work unit).
- Running `sdd-apply`, creating the GitHub repo, commits, branches or PRs (S13).

## Capabilities

> Contract with `sdd-spec`. Repository is greenfield, so all four are new.

### New Capabilities

- `mm1-theory`: theoretical M/M/1 metrics (`rho`, `L`, `Lq`, `W`, `Wq`) and the
  stability condition `lambda < mu`, including the guide §5.1 typo decision.
- `mm1-simulation`: SimPy engine (FIFO, single server), customer records, queue
  trace, the three guide scenarios, replications with CI95 and relative error.
- `mm1-reporting`: comparison table (CSV + LaTeX) and the queue/wait/
  theory-vs-simulation charts.
- `mm1-delivery`: `python -m mm1` CLI, the Streamlit interactive resource, the
  technical document with the 10 control questions and demo video, and the
  team work division.

### Modified Capabilities

- None.

## Approach

One package `src/mm1` with a fixed public interface, consumed by a single CLI
entry point and by `app/streamlit_app.py`. Theory formulas are implemented first
and become the oracle for the simulator; the simulator emits immutable records
and traces; analysis summarizes replications; reporting renders tables and
charts; delivery exposes everything through CLI + Streamlit. Work is split into
four disjoint member slices so four agents can run in parallel without conflicts.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/**` | New | SDD config, state, proposal, delta specs, design, tasks |
| `docs/division-trabajo.md` | New | Spanish work division for the four members |
| `.atl/skill-registry.md` | New | Indexed skill paths for delegated agents |
| `src/mm1/**` | New (planned) | Package: metrics, simulation, scenarios, analysis, tables, charts, cli |
| `app/streamlit_app.py` | New (planned) | Interactive resource (Domenica Rojas) |
| `tests/**` | New (planned) | One pytest module per source module |
| `reports/**`, `outputs/**` | New (planned) | Technical document, figures, regenerable CSV/PNG |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Guide §5.1 prints `rho = mu / lambda`, contradicting its own `lambda < mu` | High | Implement `rho = lambda / mu`; document as decision D1 in `design.md` and in the report |
| Long simulation of scenario 3 (lambda = 2.9) is slow or unstable-looking | Med | Replications with fixed seeds; warmup parameter; CI95 instead of single runs |
| Four parallel agents collide on shared files | Med | Disjoint ownership per slice; `__init__.py` exports frozen by the foundation slice |
| Chart test flakiness (rendering, fonts, backends) | Med | Force `Agg` backend; assert file existence/type/size, never pixels |
| Implementation exceeds the 400-line review budget | High | Chained PRs (stacked-to-main), one member slice per PR, forecast in `tasks.md` |

## Rollback Plan

Planning artifacts are additive and isolated to `openspec/**`, `docs/division-trabajo.md`
and `.atl/skill-registry.md`; reverting the planning commit removes them with no
runtime impact. No source, dependency or config file outside those paths is touched.

## Dependencies

- The signed guide text at `docs/guia/ape3_guia_simulacion_semana3.txt` (S1–S9).
- Foundation slice (package skeleton, `pyproject.toml`, `requirements.txt`) landed
  by the orchestrator before the four member slices start.
- `pytest` as declared runner; `SimPy`, `NumPy`, `Matplotlib`, `pandas`, `Streamlit`.

## Success Criteria

- [ ] `openspec/config.yaml`, `state.yaml`, `proposal.md`, four delta specs, `design.md` and `tasks.md` exist and cross-reference each other.
- [ ] All 15 feature specs (S1–S15) are traceable to at least one requirement and scenario.
- [ ] Every task names files, interface, acceptance check and spec ids (S14).
- [ ] `docs/division-trabajo.md` assigns disjoint files to the four members with branch/PR policy.
- [ ] The `rho = lambda / mu` deviation is documented as a design decision.
