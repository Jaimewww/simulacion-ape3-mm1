"""Statistical comparison of simulated runs against theory.

Owner: Richard Chamba.
Specs: S6 (theoretical vs simulated comparison), S7 (expected analysis).

This module aggregates replications per scenario and computes confidence
intervals and relative errors against the closed-form M/M/1 measures.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import copysign, exp, isfinite, lgamma, log, log1p, sqrt
from statistics import fmean, stdev

from .metrics import TheoryMetrics, theoretical_metrics
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


def _regularized_beta(x: float, a: float, b: float) -> float:
    """Evaluate I_x(a,b) by a continued fraction with symmetry for convergence."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    if x > (a + 1) / (a + b + 2):
        return 1 - _regularized_beta(1 - x, b, a)

    def nonzero(value: float) -> float:
        return value if abs(value) >= 1e-300 else copysign(1e-300, value)

    c = 1.0
    d = 1 / nonzero(1 - (a + b) * x / (a + 1))
    fraction = d
    for m in range(1, 501):
        even = m * (b - m) * x / ((a + 2 * m - 1) * (a + 2 * m))
        odd = -(a + m) * (a + b + m) * x / ((a + 2 * m) * (a + 2 * m + 1))
        for coefficient in (even, odd):
            d = 1 / nonzero(1 + coefficient * d)
            c = nonzero(1 + coefficient / c)
            delta = c * d
            fraction *= delta
        if abs(delta - 1) < 1e-14:
            scale = exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * log(x) + b * log1p(-x))
            return scale * fraction / a
    raise ArithmeticError("Student-t beta fraction did not converge")


def _student_t_critical(confidence: float, df: int) -> float:
    """Invert the Student-t beta relation for a central two-sided probability."""

    def below_quantile(t: float) -> bool:
        if confidence < 0.5:
            central = _regularized_beta(t * t / (df + t * t), 0.5, df / 2)
            return central < confidence
        tail = 0.5 * _regularized_beta(df / (df + t * t), df / 2, 0.5)
        return tail > (1 - confidence) / 2

    low, high = 0.0, 1.0
    while below_quantile(high):
        high *= 2
    for _ in range(100):
        middle = (low + high) / 2
        if below_quantile(middle):
            low = middle
        else:
            high = middle
    return (low + high) / 2


# SPEC: S7 — confidence interval of a sample.
def confidence_interval(values: Sequence[float], confidence: float = 0.95) -> tuple[float, float]:
    """Return the two-sided Student-t interval of the sample mean (D15).

    Args:
        values: Observed samples.
        confidence: Confidence level in ``(0, 1)``.

    Returns:
        The ``(lower, upper)`` bounds; a singleton has coincident bounds.

    Raises:
        ValueError: For empty/non-finite observations or confidence outside (0, 1).
    """
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if not values or not all(isfinite(value) for value in values):
        raise ValueError("values must contain finite observations")
    mean = fmean(values)
    if len(values) == 1:
        return mean, mean
    deviation = stdev(values)
    if deviation == 0:
        return mean, mean
    margin = _student_t_critical(confidence, len(values) - 1) * deviation / sqrt(len(values))
    return mean - margin, mean + margin


# SPEC: S6, S7 — relative error between a simulated and a theoretical value.
def relative_error(simulated: float, theoretical: float) -> float:
    """Return the relative error of ``simulated`` against ``theoretical``.

    Args:
        simulated: Value obtained from the simulation.
        theoretical: Value predicted by the analytical model.

    Returns:
        The relative error between both values.

    Raises:
        ValueError: If the theoretical value is zero.
    """
    if theoretical == 0:
        raise ValueError("relative error is undefined for zero theory")
    return abs(simulated - theoretical) / abs(theoretical)


def _group_runs(runs: Sequence[ScenarioRun]) -> dict[int, list[ScenarioRun]]:
    """Group replications while rejecting incompatible rates for the same id."""
    if not runs:
        raise ValueError("runs must not be empty")
    groups: dict[int, list[ScenarioRun]] = {}
    for run in runs:
        peers = groups.setdefault(run.scenario, [])
        if peers and (run.lam, run.mu) != (peers[0].lam, peers[0].mu):
            raise ValueError("a scenario must use consistent rates")
        peers.append(run)
    return groups


# SPEC: S6, S7 — aggregate runs into per-scenario summaries.
def summarize(runs: Sequence[ScenarioRun]) -> list[ScenarioSummary]:
    """Aggregate ``runs`` into one :class:`ScenarioSummary` per scenario.

    Args:
        runs: Simulated runs, possibly spanning several scenarios.

    Returns:
        The per-scenario summaries.

    Raises:
        ValueError: If runs are empty or a scenario contains inconsistent rates.
    """
    summaries = []
    for scenario, peers in sorted(_group_runs(runs).items()):
        first = peers[0]
        theory = theoretical_metrics(first.lam, first.mu)
        waits = [run.mean_wait for run in peers]
        mean_wait = fmean(waits)
        mean_queue = fmean(run.mean_queue for run in peers)
        mean_in_system = fmean(run.mean_in_system for run in peers)
        mean_system_time = fmean(run.mean_system_time for run in peers)
        summaries.append(
            ScenarioSummary(
                scenario=scenario,
                lam=first.lam,
                mu=first.mu,
                replications=len(peers),
                theory=theory,
                sim_mean_wait=mean_wait,
                sim_mean_queue=mean_queue,
                sim_mean_in_system=mean_in_system,
                sim_utilization=fmean(run.utilization for run in peers),
                std_wait=stdev(waits) if len(waits) > 1 else 0.0,
                ci95_wait=confidence_interval(waits),
                rel_error_L=relative_error(mean_in_system, theory.L),
                rel_error_Lq=relative_error(mean_queue, theory.Lq),
                rel_error_W=relative_error(mean_system_time, theory.W),
                rel_error_Wq=relative_error(mean_wait, theory.Wq),
            )
        )
    return summaries
