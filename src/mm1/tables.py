"""Tabular comparison of theory and simulation.

Owner: Cael Soto.
Specs: S6 (compare results with a table), S7 (comparison deliverable).

This module turns the per-scenario summaries into a pandas DataFrame and
exports it as CSV and LaTeX for the technical report.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from .analysis import ScenarioSummary

if TYPE_CHECKING:
    import pandas  # pyright: ignore[reportMissingImports]


# SPEC: S6 — build the theory-versus-simulation comparison table.
def comparison_dataframe(summaries: Sequence[ScenarioSummary]) -> pandas.DataFrame:
    """Build the theory-versus-simulation comparison table.

    Args:
        summaries: Per-scenario summaries to compare.

    Returns:
        A DataFrame with one row per scenario and the theoretical and
        simulated measures side by side.
    """
    raise NotImplementedError("Cael Soto — see openspec plan")


# SPEC: S6 — export the comparison table as CSV.
def write_csv(df: pandas.DataFrame, path: str | Path) -> Path:
    """Write ``df`` as a CSV file and return the written path.

    Args:
        df: Comparison table to export.
        path: Destination path for the CSV file.

    Returns:
        The path of the written file.
    """
    raise NotImplementedError("Cael Soto — see openspec plan")


# SPEC: S6, S7 — export the comparison table as LaTeX.
def to_latex(df: pandas.DataFrame, path: str | Path) -> Path:
    """Write ``df`` as a LaTeX table and return the written path.

    Args:
        df: Comparison table to export.
        path: Destination path for the LaTeX file.

    Returns:
        The path of the written file.
    """
    raise NotImplementedError("Cael Soto — see openspec plan")
