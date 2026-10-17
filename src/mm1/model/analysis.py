"""Análisis estadístico: compara simulación con teoría.

Calcula promedios, desviación, intervalo de confianza al 95% (t-Student)
y errores relativos para cada escenario.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import copysign, exp, isfinite, lgamma, log, log1p, sqrt
from statistics import fmean, stdev

from .metrics import TheoryMetrics, theoretical_metrics
from .simulation import ScenarioRun


@dataclass(frozen=True)
class ScenarioSummary:
    """Resumen teórico vs simulado para un escenario."""

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
    raise ArithmeticError("La fracción beta de Student-t no convergió")


def _student_t_critical(confidence: float, df: int) -> float:
    """Obtiene el valor crítico t para intervalo de confianza bilateral."""

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


def confidence_interval(values: Sequence[float], confidence: float = 0.95) -> tuple[float, float]:
    """Calcula intervalo de confianza al 95% (t-Student) para la media muestral.
    Se usa sobre las medias por réplica (no sobre todos los clientes).
    """
    if not 0 < confidence < 1:
        raise ValueError("la confianza debe estar entre 0 y 1")
    if not values or not all(isfinite(value) for value in values):
        raise ValueError("Los valores deben contener observaciones finitas")
    mean = fmean(values)
    if len(values) == 1:
        return mean, mean
    deviation = stdev(values)
    if deviation == 0:
        return mean, mean
    margin = _student_t_critical(confidence, len(values) - 1) * deviation / sqrt(len(values))
    return mean - margin, mean + margin


def relative_error(simulated: float, theoretical: float) -> float:
    """Calcula error relativo: |sim - teo| / |teo|."""
    if theoretical == 0:
        raise ValueError("relative error is undefined for zero theory")
    return abs(simulated - theoretical) / abs(theoretical)


def _group_runs(runs: Sequence[ScenarioRun]) -> dict[int, list[ScenarioRun]]:
    """Agrupa réplicas por escenario y verifica que las tasas sean consistentes."""
    if not runs:
        raise ValueError("Las ejecuciones no deben estar vacías")
    groups: dict[int, list[ScenarioRun]] = {}
    for run in runs:
        peers = groups.setdefault(run.scenario, [])
        if peers and (run.lam, run.mu) != (peers[0].lam, peers[0].mu):
            raise ValueError("a scenario must use consistent rates")
        peers.append(run)
    return groups


def summarize(runs: Sequence[ScenarioRun]) -> list[ScenarioSummary]:
    """Agrupa las corridas por escenario y genera un resumen para cada uno."""
    summaries = []
    for scenario, peers in sorted(_group_runs(runs).items()):
        first = peers[0]
        theory = theoretical_metrics(first.lam, first.mu)
        waits = [run.mean_wait for run in peers]  # medias por réplica
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
