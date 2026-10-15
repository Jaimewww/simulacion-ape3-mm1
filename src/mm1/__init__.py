"""M/M/1 queue simulation package (APE 003 — Simulación, 5.º ciclo FEIRNNR).

Simulación de un sistema de líneas de espera M/M/1 mediante SimPy, structured as
MVC:

* ``mm1.model`` — the domain: theory, SimPy engine, scenarios, statistics.
* ``mm1.view`` — the renderers: Matplotlib figures, comparison tables, Streamlit.
* ``mm1.controller`` — the orchestration shared by the CLI and the web page.

This package re-exports the frozen public API used by the CLI, the Streamlit app
and the tests. Importing it only binds names: it performs no simulation, no I/O
and no computation, and it does not import Streamlit.

Owners:
    - Jaime Landazuri: ``model/simulation.py``, ``controller/cli.py``.
    - Richard Chamba: ``model/metrics.py``, ``model/scenarios.py``,
      ``model/analysis.py``, ``controller/study.py``.
    - Cael Soto: ``view/tables.py``, ``view/charts.py``.
    - Domenica Rojas: ``view/streamlit_view.py``, ``app/streamlit_app.py``,
      ``reports/**``.
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
