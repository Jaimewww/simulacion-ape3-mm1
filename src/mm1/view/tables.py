"""Tabular comparison of theory and simulation.

Owner: Cael Soto.
Specs: S6 (compare results with a table), S7 (comparison deliverable).

This module turns the per-scenario summaries into a pandas DataFrame and
exports it as CSV and LaTeX for the technical report.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas

from ..model.analysis import ScenarioSummary

# SPEC: S6 — the frozen 19-column schema, in the frozen order.
COLUMNS = (
    "scenario",
    "lam",
    "mu",
    "rho",
    "L",
    "Lq",
    "W",
    "Wq",
    "sim_mean_wait",
    "sim_mean_queue",
    "sim_mean_in_system",
    "sim_utilization",
    "std_wait",
    "ci95_low",
    "ci95_high",
    "rel_error_L",
    "rel_error_Lq",
    "rel_error_W",
    "rel_error_Wq",
)

# SPEC: S6, S7 — the report references the exported float with \ref{tab:comparacion}.
LATEX_CAPTION = "Comparación de resultados teóricos y simulados por escenario"
LATEX_LABEL = "tab:comparacion"
LATEX_FLOAT_FORMAT = "%.4f"


# SPEC: S6 — build the theory-versus-simulation comparison table.
def comparison_dataframe(summaries: Sequence[ScenarioSummary]) -> pandas.DataFrame:
    """Build the theory-versus-simulation comparison table.

    Args:
        summaries: Per-scenario summaries to compare.

    Returns:
        A DataFrame with one row per scenario, ordered by scenario id, carrying
        the theoretical measures, the simulated ones, the Student-t interval
        of the simulated mean wait and the relative errors (decision D15: the
        interval is taken over the per-replication means, never over the
        individual customer waits).
    """
    rows = [
        {
            "scenario": summary.scenario,
            "lam": summary.lam,
            "mu": summary.mu,
            "rho": summary.theory.rho,
            "L": summary.theory.L,
            "Lq": summary.theory.Lq,
            "W": summary.theory.W,
            "Wq": summary.theory.Wq,
            "sim_mean_wait": summary.sim_mean_wait,
            "sim_mean_queue": summary.sim_mean_queue,
            "sim_mean_in_system": summary.sim_mean_in_system,
            "sim_utilization": summary.sim_utilization,
            "std_wait": summary.std_wait,
            "ci95_low": summary.ci95_wait[0],
            "ci95_high": summary.ci95_wait[1],
            "rel_error_L": summary.rel_error_L,
            "rel_error_Lq": summary.rel_error_Lq,
            "rel_error_W": summary.rel_error_W,
            "rel_error_Wq": summary.rel_error_Wq,
        }
        for summary in sorted(summaries, key=lambda item: item.scenario)
    ]
    return pandas.DataFrame(rows, columns=list(COLUMNS))


# SPEC: S6 — export the comparison table as CSV.
def write_csv(df: pandas.DataFrame, path: str | Path) -> Path:
    """Write ``df`` as a CSV file and return the written path.

    Args:
        df: Comparison table to export.
        path: Destination path for the CSV file.

    Returns:
        The path of the written file. Repeated calls overwrite the same file.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)
    return destination


# SPEC: S6, S7 — export the comparison table as LaTeX.
def to_latex(df: pandas.DataFrame, path: str | Path) -> Path:
    """Write ``df`` as a LaTeX table float and return the written path.

    The tabular body comes from pandas; the ``table`` float, the caption and
    the label are added here so the report can reference the table with
    ``\\ref{tab:comparacion}`` no matter which pandas version renders the body.

    Args:
        df: Comparison table to export.
        path: Destination path for the LaTeX file.

    Returns:
        The path of the written file. Repeated calls overwrite the same file.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tabular = df.to_latex(index=False, float_format=LATEX_FLOAT_FORMAT)
    body = (
        "\\begin{table}\n"
        "\\centering\n"
        f"{tabular}"
        f"\\caption{{{LATEX_CAPTION}}}\n"
        f"\\label{{{LATEX_LABEL}}}\n"
        "\\end{table}\n"
    )
    destination.write_text(body, encoding="utf-8")
    return destination
