"""Capa modelo: lógica y cálculos del sistema M/M/1.

Contiene métricas teóricas, simulación con SimPy, escenarios y análisis.
No depende de la vista ni del controlador.
"""

from __future__ import annotations

from .analysis import (
    ScenarioSummary,
    confidence_interval,
    relative_error,
    summarize,
)
from .metrics import TheoryMetrics, is_stable, theoretical_metrics, utilization
from .scenarios import SCENARIOS, Scenario, run_scenarios
from .simulation import CustomerRecord, ScenarioRun, run_mm1

__all__ = [
    "SCENARIOS",
    "CustomerRecord",
    "Scenario",
    "ScenarioRun",
    "ScenarioSummary",
    "TheoryMetrics",
    "confidence_interval",
    "is_stable",
    "relative_error",
    "run_mm1",
    "run_scenarios",
    "summarize",
    "theoretical_metrics",
    "utilization",
]
