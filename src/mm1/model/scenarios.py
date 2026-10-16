"""Scenario catalogue and multi-replication runner.

Owner: Richard Chamba.
Specs: S5 (the three scenarios from guide section 5.1), S6 (per-scenario records).

The catalogue holds the frozen ``(lambda, mu)`` pairs of the practice. The runner
executes every scenario several times so that later analysis can aggregate the
results.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .simulation import ScenarioRun, run_mm1


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


# SPEC: S5 — verbatim scenario labels and conditions from the guide.
SCENARIOS: tuple[Scenario, ...] = (
    Scenario(1, 2.0, 3.0, "Escenario 1", "Sistema estable"),
    Scenario(2, 2.5, 3.0, "Escenario 2", "Mayor utilización"),
    Scenario(3, 2.9, 3.0, "Escenario 3", "Cerca de saturación"),
)


# SPEC: S5, S6 — run every scenario for a number of replications.
def run_scenarios(
    replications: int = 30, sim_time: float = 1000.0, base_seed: int = 42, warmup: float = 0.0
) -> list[ScenarioRun]:
    """Run every scenario ``replications`` times and return the runs.

    Args:
        replications: Number of independent replications per scenario.
        sim_time: Total simulated time per replication.
        base_seed: Base seed from which per-replication seeds are derived.
        warmup: Warm-up period discarded from each replication's statistics.

    Returns:
        Runs in catalogue order, then replication order within each scenario.

    Raises:
        ValueError: If the replication count or simulation parameters are invalid.
    """
    if isinstance(replications, bool) or not isinstance(replications, int) or replications < 1:
        raise ValueError("replications must be a positive integer")
    runs = []
    for scenario in SCENARIOS:
        for replication in range(replications):
            # Stable across processes, catalogue order and replication counts.
            key = f"{base_seed}:{scenario.id}:{replication}".encode("ascii")
            seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
            runs.append(
                run_mm1(
                    scenario.lam,
                    scenario.mu,
                    sim_time=sim_time,
                    seed=seed,
                    scenario=scenario.id,
                    warmup=warmup,
                )
            )
    return runs
