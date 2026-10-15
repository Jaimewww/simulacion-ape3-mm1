"""Scenario catalogue and multi-replication runner.

Owner: Richard Chamba.
Specs: S5 (the three scenarios from guide section 5.1), S6 (per-scenario records).

The catalogue holds the frozen ``(lambda, mu)`` pairs of the practice. The runner
executes every scenario several times so that later analysis can aggregate the
results.
"""

from __future__ import annotations

from dataclasses import dataclass

from .simulation import ScenarioRun


# SPEC: S5 — one entry of the scenario table in guide section 5.1.
@dataclass(frozen=True)
class Scenario:
    """A frozen M/M/1 scenario from the practice guide.

    Attributes:
        id: Scenario number (1, 2 or 3).
        lam: Average arrival rate ``lambda``.
        mu: Average service rate ``mu``.
        label: Short Spanish label of the scenario.
        condition: Spanish description of the operating condition.
    """

    id: int
    lam: float
    mu: float
    label: str
    condition: str


# SPEC: S5 — populated by Richard Chamba; placeholder keeps imports side-effect free.
SCENARIOS: tuple[Scenario, ...] = ()


# SPEC: S5, S6 — run every scenario for a number of replications.
def run_scenarios(
    replications: int = 30, sim_time: float = 1000.0, base_seed: int = 42, warmup: float = 0.0
) -> ScenarioRun | list[ScenarioRun]:
    """Run every scenario ``replications`` times and return the runs.

    Args:
        replications: Number of independent replications per scenario.
        sim_time: Total simulated time per replication.
        base_seed: Base seed from which per-replication seeds are derived.
        warmup: Warm-up period discarded from each replication's statistics.

    Returns:
        A single :class:`ScenarioRun` or the list of runs produced.
    """
    raise NotImplementedError("Richard Chamba — see openspec plan")
