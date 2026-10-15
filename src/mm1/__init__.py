"""M/M/1 queue simulation package (APE 003 — Simulación, 5.º ciclo FEIRNNR).

Simulación de un sistema de líneas de espera M/M/1 mediante SimPy. This package
re-exports the frozen public API used by the CLI, the Streamlit app and the
tests. Importing it only binds names: it performs no simulation, no I/O and no
computation. The Streamlit landing page and the CLI consume this same API.

Owners:
    - Jaime Landazuri: ``simulation``, ``cli``.
    - Richard Chamba: ``metrics``, ``scenarios``, ``analysis``.
    - Cael Soto: ``tables``, ``charts``.
    - Domenica Rojas: ``app/streamlit_app.py``, ``reports/**``.
"""

from __future__ import annotations

from .analysis import (
    ScenarioSummary,
    confidence_interval,
    relative_error,
    summarize,
)
from .charts import (
    generate_all,
    plot_queue_evolution,
    plot_scenario_comparison,
    plot_theory_vs_sim,
    plot_wait_times,
)
from .cli import main
from .metrics import TheoryMetrics, is_stable, theoretical_metrics, utilization
from .scenarios import SCENARIOS, Scenario, run_scenarios
from .simulation import CustomerRecord, ScenarioRun, run_mm1
from .tables import comparison_dataframe, to_latex, write_csv

__all__ = [
    "SCENARIOS",
    "CustomerRecord",
    "Scenario",
    "ScenarioRun",
    "ScenarioSummary",
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
    "summarize",
    "theoretical_metrics",
    "to_latex",
    "utilization",
    "write_csv",
]
