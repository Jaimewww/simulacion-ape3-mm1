"""Paquete para simular un sistema M/M/1 con SimPy.

Reexporta las funciones y clases más usadas desde el modelo, el controlador
y la vista, para poder importarlas desde `mm1.*`.
"""

from __future__ import annotations

from .controller import StudyResult, main, run_study
from .model import (
    SCENARIOS,
    CustomerRecord,
    Scenario,
    ScenarioRun,
    ScenarioSummary,
    TheoryMetrics,
    confidence_interval,
    is_stable,
    relative_error,
    run_mm1,
    run_scenarios,
    summarize,
    theoretical_metrics,
    utilization,
)
from .view import (
    comparison_dataframe,
    generate_all,
    plot_queue_evolution,
    plot_scenario_comparison,
    plot_theory_vs_sim,
    plot_wait_times,
    to_latex,
    write_csv,
)

__all__ = [
    "SCENARIOS",
    "CustomerRecord",
    "Scenario",
    "ScenarioRun",
    "ScenarioSummary",
    "StudyResult",
    "TheoryMetrics",
    "comparison_dataframe",
    "confidence_interval",
    "generate_all",
    "is_stable",
    "main",
    "plot_queue_evolution",
    "plot_scenario_comparison",
    "plot_theory_vs_sim",
    "plot_wait_times",
    "relative_error",
    "run_mm1",
    "run_scenarios",
    "run_study",
    "summarize",
    "theoretical_metrics",
    "to_latex",
    "utilization",
    "write_csv",
]
