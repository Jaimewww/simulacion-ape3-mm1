"""View layer — every renderer, with no domain computation.

Owner: Cael Soto (charts, tables) and Domenica Rojas (the Streamlit page).
Specs: S6, S7, S11, S16.

This package is the ``V`` of the MVC structure. Every module here turns model
data into something a human reads: a Matplotlib figure, a comparison table, or
the interactive Streamlit page. Views MUST NOT compute domain results; they call
``mm1.controller`` for that.

``streamlit_view`` is deliberately NOT re-exported here: importing it pulls in
Streamlit, and ``import mm1`` must stay dependency-free.
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
