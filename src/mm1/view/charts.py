"""Gráficos para el sistema M/M/1.

Genera: evolución de la cola, tiempos de espera, comparación teoría vs simulada
y comparación entre escenarios. Usa backend no interactivo (Agg).
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib

# Backend sin interfaz gráfica (para guardar archivos)
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from ..model.analysis import ScenarioSummary
from ..model.simulation import ScenarioRun

# Resolución de las gráficas
DPI = 150

# Nombres de archivos
QUEUE_SUFFIX = "cola"
WAIT_SUFFIX = "espera"
THEORY_FIGURE = "teoria_vs_simulacion.png"
COMPARISON_FIGURE = "comparacion_escenarios.png"


def _save_figure(fig: Figure, path: str | Path) -> Path:
    """Guarda la gráfica y la cierra para no dejar figuras abiertas."""
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return Path(path)


def _ci95_errors(summaries: Sequence[ScenarioSummary]) -> list[list[float]]:
    """Devuelve errores para barras con IC95 (inferior, superior)."""
    return [
        [summary.sim_mean_wait - summary.ci95_wait[0] for summary in summaries],
        [summary.ci95_wait[1] - summary.sim_mean_wait for summary in summaries],
    ]


def plot_queue_evolution(run: ScenarioRun, path: str | Path) -> Path:
    """Grafica la evolución de la longitud de cola a lo largo del tiempo."""
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


def plot_wait_times(run: ScenarioRun, path: str | Path) -> Path:
    """Grafica los tiempos de espera de cada cliente a lo largo de las llegadas."""
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


def plot_theory_vs_sim(summaries: Sequence[ScenarioSummary], path: str | Path) -> Path:
    """Grafica teoría vs simulación con barras (incluye IC95% para Wq)."""
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


def generate_all(
    runs: Sequence[ScenarioRun], summaries: Sequence[ScenarioSummary], out_dir: str | Path
) -> list[Path]:
    """Genera todas las gráficas necesarias en el directorio indicado."""
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
