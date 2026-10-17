"""Catálogo de escenarios y ejecución con varias réplicas."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .simulation import ScenarioRun, run_mm1


@dataclass(frozen=True)
class Scenario:
    """Escenario definido en la guía práctica."""

    id: int
    lam: float  # tasa de llegadas λ
    mu: float   # tasa de servicio μ
    label: str
    condition: str


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(1, 2.0, 3.0, "Escenario 1", "Sistema estable"),
    Scenario(2, 2.5, 3.0, "Escenario 2", "Mayor utilización"),
    Scenario(3, 2.9, 3.0, "Escenario 3", "Cerca de saturación"),
)


def run_scenarios(
    replications: int = 30, sim_time: float = 1000.0, base_seed: int = 42, warmup: float = 0.0
) -> list[ScenarioRun]:
    """Ejecuta cada escenario varias veces y devuelve todas las corridas."""
    if isinstance(replications, bool) or not isinstance(replications, int) or replications < 1:
        raise ValueError("replications must be a positive integer")
    runs = []
    for scenario in SCENARIOS:
        for replication in range(replications):
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
