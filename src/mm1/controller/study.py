"""Servicio para ejecutar el estudio con los tres escenarios de la guía.

Agrupa las repeticiones de cada escenario, calcula promedios y errores
relativos. Es usado por el CLI y por las funciones que generan tablas/gráficos.
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
    """Resultado completo del estudio con los tres escenarios."""

    runs: tuple[ScenarioRun, ...]  # Todas las réplicas, ordenadas por escenario y réplicas
    summaries: tuple[ScenarioSummary, ...]  # Resumen por escenario


def run_study(
    replications: int = 30,
    sim_time: float = 1000.0,
    base_seed: int = 42,
    warmup: float = 0.0,
) -> StudyResult:
    """Ejecuta los tres escenarios con varias réplicas.
    Devuelve corridas y resumen teórico vs simulado por escenario.
    """
    runs = run_scenarios(replications, sim_time, base_seed, warmup)
    return StudyResult(runs=tuple(runs), summaries=tuple(summarize(runs)))
