"""Model layer — the M/M/1 domain, with no rendering and no I/O.

Owner: Richard Chamba (metrics, scenarios, analysis) and Jaime Landazuri
(simulation).
Specs: S3, S4, S5, S6, S16.

This package is the ``M`` of the MVC structure. It answers questions about the
queueing system and knows nothing about charts, tables, Streamlit or the
command line. It MUST NOT import ``mm1.view`` or ``mm1.controller``.
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
