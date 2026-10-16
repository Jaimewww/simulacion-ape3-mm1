"""Application service that runs the three-scenario study.

Owner: Richard Chamba.
Specs: S5 (the three scenarios), S6 (per-scenario metrics), S14 (agent-executable
entry point), S16 (controller layer).

This is the ``C`` that every entry point shares: ``mm1.controller.cli`` and the
renderers call ``run_study`` and render the same numbers. Keeping a single
entry point is what prevents the document's figures from diverging from the
generated artifacts. The result carries model data only — no ``pandas``, no web
framework — so the controller never depends on the view.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..model import ScenarioRun, ScenarioSummary, run_scenarios, summarize

__all__ = [
    "StudyResult",
    "run_study",
]


@dataclass(frozen=True)
class StudyResult:
    """Everything one full study run produced.

    Attributes:
        runs: Every replication of every scenario, in scenario then replication
            order (``SCENARIOS`` order, ``replications`` each).
        summaries: One aggregated summary per scenario, in ``SCENARIOS`` order.
    """

    runs: tuple[ScenarioRun, ...]
    summaries: tuple[ScenarioSummary, ...]


# SPEC: S5, S6, S16 — simulate every scenario, then aggregate theory vs simulation.
def run_study(
    replications: int = 30,
    sim_time: float = 1000.0,
    base_seed: int = 42,
    warmup: float = 0.0,
) -> StudyResult:
    """Run the full three-scenario study and aggregate it.

    Args:
        replications: Independent replications per scenario.
        sim_time: Simulated time per replication.
        base_seed: Seed for the first replication; later replications derive
            from it so the whole study is reproducible.
        warmup: Transient period excluded from the statistics.

    Returns:
        A :class:`StudyResult` with the runs and the per-scenario summaries.

    Raises:
        ValueError: If any scenario is unstable (``lam >= mu``).
    """
    runs = run_scenarios(replications, sim_time, base_seed, warmup)
    return StudyResult(runs=tuple(runs), summaries=tuple(summarize(runs)))
