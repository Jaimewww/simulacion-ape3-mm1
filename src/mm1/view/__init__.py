"""View layer — every renderer, with no domain computation.

Owner: Cael Soto (charts, tables) and Domenica Rojas (the queue animation).
Specs: S6, S7, S16, S19.

This package is the ``V`` of the MVC structure. Every module here turns model
data into something a human reads: a Matplotlib figure, a comparison table, or
the animated queue evolution. Views MUST NOT compute domain results; they call
``mm1.controller`` for that.

``animation`` is deliberately NOT re-exported here: importing it pulls in the
animation stack, and ``import mm1`` must stay dependency-free. There is no web
view: the practice has no interactive interface (S19).
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
