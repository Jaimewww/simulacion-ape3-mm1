"""Charts for the M/M/1 practice.

Owner: Cael Soto.
Specs: S7 (queue behaviour and wait-time charts, theory-vs-simulation comparison).

This module renders the figures required by the guide: queue evolution, waiting
times, theory-versus-simulation and scenario comparison. It only writes image
files under the requested output directory.

Rendering rules frozen by the plan:

* The non-interactive ``Agg`` backend is forced at module level, **before**
  pyplot is imported, so no figure ever needs a display (decision D6) even
  when another module imported pyplot first.
* Every function closes its figure after saving it, so repeated calls never
  accumulate open figures.
* Axis labels, titles and legends are in Spanish because the figures go into
  the report; the code and its identifiers stay in English.
* Figures carry no dates or timestamps, so the same inputs always render the
  same image.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib

# Decision D6: headless backend, set before pyplot is imported. The call
# deliberately sits between the two imports.
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from ..model.analysis import ScenarioSummary
from ..model.simulation import ScenarioRun

# Resolution of the saved figures; high enough for the report, no timestamps.
DPI = 150

# File names written by generate_all (Spanish: they are report artifacts, like
# the CLI's own comparacion.csv).
QUEUE_SUFFIX = "cola"
WAIT_SUFFIX = "espera"
THEORY_FIGURE = "teoria_vs_simulacion.png"
COMPARISON_FIGURE = "comparacion_escenarios.png"


def _save_figure(fig: Figure, path: str | Path) -> Path:
    """Save ``fig`` to ``path`` and close it so nothing accumulates."""
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return Path(path)


def _ci95_errors(summaries: Sequence[ScenarioSummary]) -> list[list[float]]:
    """Student-t interval of the mean wait as (lower, upper) error-bar lists."""
    return [
        [summary.sim_mean_wait - summary.ci95_wait[0] for summary in summaries],
        [summary.ci95_wait[1] - summary.sim_mean_wait for summary in summaries],
    ]


# SPEC: S7 — queue-size evolution over simulated time.
def plot_queue_evolution(run: ScenarioRun, path: str | Path) -> Path:
    """Plot the queue size over time for ``run`` and save it to ``path``.

    The queue trace is piecewise constant, so it is drawn as a step function
    closed at the simulated horizon, next to the run's average queue length.

    Args:
        run: Simulation run whose ``queue_trace`` is plotted.
        path: Destination path for the image.

    Returns:
        The path of the written image.
    """
    times = [float(time) for time, _ in run.queue_trace]
    lengths = [float(length) for _, length in run.queue_trace]
    if not times:
        times, lengths = [0.0], [0.0]
    times.append(run.sim_time)
    lengths.append(lengths[-1])

    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.step(times, lengths, where="post", label="Largo de la cola")
    ax.axhline(run.mean_queue, linestyle="--", label=f"Promedio simulado ({run.mean_queue:.2f})")
    ax.set_xlabel("Tiempo simulado")
    ax.set_ylabel("Clientes en la cola")
    ax.set_title(f"Evolución de la cola — Escenario {run.scenario} (λ={run.lam:g}, μ={run.mu:g})")
    ax.legend()
    return _save_figure(fig, path)


# SPEC: S7 — distribution of customer waiting times.
def plot_wait_times(run: ScenarioRun, path: str | Path) -> Path:
    """Plot the customer waiting times of ``run`` and save it to ``path``.

    Args:
        run: Simulation run whose customer records are plotted.
        path: Destination path for the image.

    Returns:
        The path of the written image.
    """
    arrivals = [customer.arrival_time for customer in run.customers]
    waits = [customer.wait_time for customer in run.customers]

    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.plot(arrivals, waits, linewidth=1.0, label="Espera de cada cliente")
    ax.axhline(run.mean_wait, linestyle="--", label=f"Promedio simulado ({run.mean_wait:.2f})")
    ax.set_xlabel("Tiempo de llegada del cliente")
    ax.set_ylabel("Tiempo de espera en la cola")
    ax.set_title(
        f"Tiempos de espera por cliente — Escenario {run.scenario} (λ={run.lam:g}, μ={run.mu:g})"
    )
    ax.legend()
    return _save_figure(fig, path)


# SPEC: S7 — theory-versus-simulation comparison chart.
def plot_theory_vs_sim(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path:
    """Plot theory against simulation for ``summaries`` and save it to ``path``.

    One panel per measure (ρ, L, Lq, Wq) with two bars per scenario. The Wq
    panel adds the 95 % Student-t interval of the simulated mean, which is the
    evidence that the theory falls inside the interval (decision D15).

    Args:
        summaries: Per-scenario summaries to compare.
        path: Destination path for the image.

    Returns:
        The path of the written image.
    """
    ordered = sorted(summaries, key=lambda item: item.scenario)
    ids = [summary.scenario for summary in ordered]
    wait_errors = _ci95_errors(ordered)
    panels = (
        (
            "Utilización ρ",
            [s.theory.rho for s in ordered],
            [s.sim_utilization for s in ordered],
            None,
        ),
        (
            "Clientes en el sistema (L)",
            [s.theory.L for s in ordered],
            [s.sim_mean_in_system for s in ordered],
            None,
        ),
        (
            "Clientes en la cola (Lq)",
            [s.theory.Lq for s in ordered],
            [s.sim_mean_queue for s in ordered],
            None,
        ),
        (
            "Espera en la cola (Wq)",
            [s.theory.Wq for s in ordered],
            [s.sim_mean_wait for s in ordered],
            wait_errors,
        ),
    )

    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.0), constrained_layout=True)
    positions = range(len(ordered))
    width = 0.38
    for ax, (title, theory, simulated, errors) in zip(axes.flat, panels):
        ax.bar([i - width / 2 for i in positions], theory, width, label="Teórico")
        ax.bar(
            [i + width / 2 for i in positions],
            simulated,
            width,
            yerr=errors,
            capsize=3,
            label="Simulado (IC 95 %)" if errors else "Simulado",
        )
        ax.set_xticks(list(positions))
        ax.set_xticklabels([f"Esc. {scenario}" for scenario in ids])
        ax.set_title(title)
        ax.legend()
    fig.suptitle("Teoría vs. simulación por escenario")
    return _save_figure(fig, path)


# SPEC: S7 — side-by-side comparison of the three scenarios.
def plot_scenario_comparison(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path:
    """Plot the comparison of scenarios in ``summaries`` and save it to ``path``.

    Both panels answer guide section 6: as λ approaches μ (ρ grows), the
    waiting time and the queue length grow towards their theoretical values.

    Args:
        summaries: Per-scenario summaries to compare.
        path: Destination path for the image.

    Returns:
        The path of the written image.
    """
    ordered = sorted(summaries, key=lambda item: item.scenario)
    rho = [summary.theory.rho for summary in ordered]
    wait_errors = _ci95_errors(ordered)

    fig, (wait_ax, queue_ax) = plt.subplots(
        1, 2, figsize=(10.0, 4.5), constrained_layout=True, sharex=True
    )

    wait_ax.plot(rho, [s.theory.Wq for s in ordered], "o--", label="Teórico")
    wait_ax.errorbar(
        rho,
        [s.sim_mean_wait for s in ordered],
        yerr=wait_errors,
        fmt="o-",
        capsize=3,
        label="Simulado (IC 95 %)",
    )
    wait_ax.set_xlabel("Utilización ρ = λ/μ")
    wait_ax.set_ylabel("Tiempo de espera en la cola")
    wait_ax.set_title("Espera en la cola")
    wait_ax.legend()

    queue_ax.plot(rho, [s.theory.Lq for s in ordered], "o--", label="Teórico")
    queue_ax.plot(rho, [s.sim_mean_queue for s in ordered], "o-", label="Simulado")
    queue_ax.set_xlabel("Utilización ρ = λ/μ")
    queue_ax.set_ylabel("Clientes en la cola")
    queue_ax.set_title("Largo de la cola")
    queue_ax.legend()

    fig.suptitle("Comparación entre escenarios")
    return _save_figure(fig, path)


# SPEC: S7 — render every chart into ``out_dir``.
def generate_all(
    runs: Sequence[ScenarioRun], summaries: Sequence[ScenarioSummary], out_dir: str | Path
) -> list[Path]:
    """Render every required chart into ``out_dir``.

    Every run gets its queue-evolution and wait-times chart, named by scenario
    and replica so repeated calls overwrite the same files; the two summary
    figures are written once each.

    Args:
        runs: Simulation runs used by the per-run charts.
        summaries: Per-scenario summaries used by the comparison charts.
        out_dir: Directory where the images are written.

    Returns:
        The list of paths of the written images.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    replicas: dict[int, int] = {}
    for run in runs:
        replica = replicas.get(run.scenario, 0) + 1
        replicas[run.scenario] = replica
        stem = f"escenario_{run.scenario}_replica_{replica}"
        paths.append(plot_queue_evolution(run, out / f"{stem}_{QUEUE_SUFFIX}.png"))
        paths.append(plot_wait_times(run, out / f"{stem}_{WAIT_SUFFIX}.png"))

    paths.append(plot_theory_vs_sim(summaries, out / THEORY_FIGURE))
    paths.append(plot_scenario_comparison(summaries, out / COMPARISON_FIGURE))
    return paths
