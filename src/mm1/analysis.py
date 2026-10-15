"""Statistical comparison of simulated runs against theory.

Owner: Richard Chamba.
Specs: S6 (theoretical vs simulated comparison), S7 (expected analysis).

This module aggregates replications per scenario and computes confidence
intervals and relative errors against the closed-form M/M/1 measures.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .metrics import TheoryMetrics
from .simulation import ScenarioRun


# SPEC: S6, S7 — summary of one scenario: theory, simulation and error.
@dataclass(frozen=True)
class ScenarioSummary:
    """Theory-versus-simulation summary of one scenario.

    Attributes:
        scenario: Scenario identifier.
        lam: Arrival rate ``lambda``.
        mu: Service rate ``mu``.
        replications: Number of replications aggregated.
        theory: Theoretical measures for the scenario.
        sim_mean_wait: Simulated average waiting time.
        sim_mean_queue: Simulated average queue length.
        sim_mean_in_system: Simulated average number of customers in the system.
        sim_utilization: Simulated server utilization.
        std_wait: Standard deviation of the simulated waiting times.
        ci95_wait: 95% confidence interval of the simulated waiting time.
        rel_error_L: Relative error of ``L`` against theory.
        rel_error_Lq: Relative error of ``Lq`` against theory.
        rel_error_W: Relative error of ``W`` against theory.
        rel_error_Wq: Relative error of ``Wq`` against theory.
    """

    scenario: int
    lam: float
    mu: float
    replications: int
    theory: TheoryMetrics
    sim_mean_wait: float
    sim_mean_queue: float
    sim_mean_in_system: float
    sim_utilization: float
    std_wait: float
    ci95_wait: tuple[float, float]
    rel_error_L: float
    rel_error_Lq: float
    rel_error_W: float
    rel_error_Wq: float


# SPEC: S7 — confidence interval of a sample.
def confidence_interval(values: Sequence[float], confidence: float = 0.95) -> tuple[float, float]:
    """Return the confidence interval of ``values``.

    Args:
        values: Observed samples.
        confidence: Confidence level in ``(0, 1)``.

    Returns:
        The ``(lower, upper)`` bounds of the interval.
    """
    raise NotImplementedError("Richard Chamba — see openspec plan")


# SPEC: S6, S7 — relative error between a simulated and a theoretical value.
def relative_error(simulated: float, theoretical: float) -> float:
    """Return the relative error of ``simulated`` against ``theoretical``.

    Args:
        simulated: Value obtained from the simulation.
        theoretical: Value predicted by the analytical model.

    Returns:
        The relative error between both values.
    """
    raise NotImplementedError("Richard Chamba — see openspec plan")


# SPEC: S6, S7 — aggregate runs into per-scenario summaries.
def summarize(runs: Sequence[ScenarioRun]) -> list[ScenarioSummary]:
    """Aggregate ``runs`` into one :class:`ScenarioSummary` per scenario.

    Args:
        runs: Simulated runs, possibly spanning several scenarios.

    Returns:
        The per-scenario summaries.
    """
    raise NotImplementedError("Richard Chamba — see openspec plan")
