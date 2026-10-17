"""Capa vista: muestra resultados (tablas y gráficos).

Convierte datos del modelo en información para leer o exportar.
No hace cálculos del dominio.
"""

from __future__ import annotations

from .charts import (
    generate_all,
    plot_queue_evolution,
    plot_scenario_comparison,
    plot_theory_vs_sim,
    plot_wait_times,
)
from .tables import comparison_dataframe, to_latex, write_csv

__all__ = [
    "comparison_dataframe",
    "generate_all",
    "plot_queue_evolution",
    "plot_scenario_comparison",
    "plot_theory_vs_sim",
    "plot_wait_times",
    "to_latex",
    "write_csv",
]
