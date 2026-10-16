# Main Specifications (source of truth)

This directory holds the merged, current behavior of the project: one subdirectory per
capability, each with a `spec.md`.

## Current state

The repository is greenfield and the first change is still active:

- Active change: `openspec/changes/ape3-mm1-queue-simulation/`
- Delta specs for that change: `openspec/changes/ape3-mm1-queue-simulation/specs/{domain}/spec.md`

`openspec/specs/` is intentionally empty of capability folders until that change is
archived. `sdd-archive` merges each delta `## ADDED Requirements` block into
`openspec/specs/{domain}/spec.md` and then moves the change folder to
`openspec/changes/archive/YYYY-MM-DD-ape3-mm1-queue-simulation/`.

## Expected capabilities after the first archive

| Capability | Purpose |
| ---------- | ------- |
| `mm1-theory` | Theoretical M/M/1 metrics (`rho`, `L`, `Lq`, `W`, `Wq`) and the stability condition `lambda < mu`. |
| `mm1-simulation` | SimPy M/M/1 engine, customer records, queue trace, the three guide scenarios, replication summaries. |
| `mm1-reporting` | Comparison table (CSV + LaTeX), queue/wait/theory-vs-simulation charts, and the headless queue animation. |
| `mm1-delivery` | `python -m mm1` CLI (the only interface, no web UI), technical document, work division. |

## Rules

- Do not edit capability specs by hand while a delta for the same capability is active.
- Every requirement keeps at least one Given/When/Then scenario.
