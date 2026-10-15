"""Charts for the M/M/1 practice.

Owner: Cael Soto.
Specs: S7 (queue behaviour and wait-time charts, theory-vs-simulation comparison).

This module renders the figures required by the guide: queue evolution, waiting
times, theory-versus-simulation and scenario comparison. It only writes image
files under the requested output directory.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ..model.analysis import ScenarioSummary
from ..model.simulation import ScenarioRun


# SPEC: S7 — queue-size evolution over simulated time.
def plot_queue_evolution(run: ScenarioRun, path: str | Path) -> Path:
    """Plot the queue size over time for ``run`` and save it to ``path``.

    Args:
        run: Simulation run whose ``queue_trace`` is plotted.
        path: Destination path for the image.

    Returns:
        The path of the written image.
    """
    raise NotImplementedError("Cael Soto — see openspec plan")


# SPEC: S7 — distribution of customer waiting times.
def plot_wait_times(run: ScenarioRun, path: str | Path) -> Path:
    """Plot the customer waiting times of ``run`` and save it to ``path``.

    Args:
        run: Simulation run whose customer records are plotted.
        path: Destination path for the image.

    Returns:
        The path of the written image.
    """
    raise NotImplementedError("Cael Soto — see openspec plan")


# SPEC: S7 — theory-versus-simulation comparison chart.
def plot_theory_vs_sim(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path:
    """Plot theory against simulation for ``summaries`` and save it to ``path``.

    Args:
        summaries: Per-scenario summaries to compare.
        path: Destination path for the image.

    Returns:
        The path of the written image.
    """
    raise NotImplementedError("Cael Soto — see openspec plan")


# SPEC: S7 — side-by-side comparison of the three scenarios.
def plot_scenario_comparison(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path:
    """Plot the comparison of scenarios in ``summaries`` and save it to ``path``.

    Args:
        summaries: Per-scenario summaries to compare.
        path: Destination path for the image.

    Returns:
        The path of the written image.
    """
    raise NotImplementedError("Cael Soto — see openspec plan")


# SPEC: S7 — render every chart into ``out_dir``.
def generate_all(
    runs: Sequence[ScenarioRun], summaries: Sequence[ScenarioSummary], out_dir: str | Path
) -> list[Path]:
    """Render every required chart into ``out_dir``.

    Args:
        runs: Simulation runs used by the per-run charts.
        summaries: Per-scenario summaries used by the comparison charts.
        out_dir: Directory where the images are written.

    Returns:
        The list of paths of the written images.
    """
    raise NotImplementedError("Cael Soto — see openspec plan")
