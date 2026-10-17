"""Punto de entrada de línea de comandos para simular M/M/1.

Este módulo permite ejecutar la simulación desde la terminal en dos modos:
- Modo simple: con --lam y --mu se hace una sola corrida y se comparan
  resultados teóricos y simulados.
- Modo por escenarios: (por defecto) corre los tres escenarios de la guía,
  genera tabla CSV/LaTeX y gráficos en la carpeta de salida.

No hay interfaz interactiva. Toda la lógica de orquestación pasa por study.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..model.metrics import is_stable, theoretical_metrics
from ..model.simulation import ScenarioRun, run_mm1
from ..view import comparison_dataframe, generate_all, to_latex, write_csv
from .study import run_study

# Directorio donde se guardan resultados (CSV, LaTeX, gráficas)
DEFAULT_OUTPUT_DIR = Path("outputs")
# Semilla base para los escenarios
DEFAULT_BASE_SEED = 42
# Códigos de salida
EXIT_OK = 0          # Todo salió bien
EXIT_UNSTABLE = 2     # Sistema no estable (λ >= μ)
EXIT_INVALID = 3      # Parámetros inválidos


def _build_parser() -> argparse.ArgumentParser:
    """Configura los argumentos de línea de comandos (CLI)."""
    parser = argparse.ArgumentParser(
        prog="mm1",
        description=(
            "Simulación de una línea de espera M/M/1. Sin argumentos corre los tres "
            "escenarios de la guía; con --lam y --mu corre una sola simulación."
        ),
    )
    parser.add_argument(
        "--lam",
        type=float,
        default=None,
        metavar="LAMBDA",
        help="tasa de llegada λ para una sola corrida",
    )
    parser.add_argument(
        "--mu",
        type=float,
        default=None,
        metavar="MU",
        help="tasa de servicio μ para una sola corrida",
    )
    parser.add_argument(
        "--scenarios",
        action="store_true",
        help="corre los tres escenarios de la guía (modo por defecto)",
    )
    parser.add_argument(
        "--replications",
        type=int,
        default=30,
        metavar="N",
        help="réplicas por escenario (por defecto 30)",
    )
    parser.add_argument(
        "--sim-time",
        type=float,
        default=1000.0,
        metavar="T",
        help="tiempo simulado por corrida (por defecto 1000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="S",
        help="semilla; en modo con escenarios es la semilla base",
    )
    parser.add_argument(
        "--warmup",
        type=float,
        default=0.0,
        metavar="W",
        help="período de calentamiento excluido de las estadísticas",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        metavar="DIR",
        help="directorio de salida para el modo con escenarios (por defecto outputs)",
    )
    return parser


def _print_single_report(lam: float, mu: float, run: ScenarioRun) -> None:
    """Muestra en consola los resultados teóricos y simulados de una sola corrida.
    Compara: tiempo en cola (Wq), tiempo en sistema (W), cola promedio (Lq),
    clientes en sistema (L) y utilización (ρ).
    """
    theory = theoretical_metrics(lam, mu)
    print(f"Corrida única M/M/1   λ={lam:g}  μ={mu:g}  ρ_teórica={theory.rho:.4f}")
    print(f"{'métrica':<14}{'teórica':>12}{'simulada':>12}{'error rel.':>12}")
    for label, expected, observed in (
        ("Wq", theory.Wq, run.mean_wait),          # tiempo promedio en cola
        ("W", theory.W, run.mean_system_time),      # tiempo promedio en sistema
        ("Lq", theory.Lq, run.mean_queue),          # longitud promedio de cola
        ("L", theory.L, run.mean_in_system),        # clientes promedio en sistema
        ("utilización", theory.rho, run.utilization),# uso del servidor
    ):
        error = abs(observed - expected) / expected if expected else 0.0
        print(f"{label:<14}{expected:>12.4f}{observed:>12.4f}{error:>11.2%}")
    print(
        f"clientes atendidos={run.n_customers}  sim_time={run.sim_time:g}"
        f"  warmup={run.warmup:g}  semilla={run.seed}"
    )


def _run_single(args: argparse.Namespace) -> int:
    """Ejecuta una sola corrida con λ y μ dados.
    Verifica estabilidad, corre simulación y muestra resultados teóricos vs simulados.
    """
    lam: float = args.lam  # tasa de llegadas
    mu: float = args.mu    # tasa de servicio
    if not is_stable(lam, mu):
        print("El sistema no es estable")
        return EXIT_UNSTABLE

    try:
        run = run_mm1(lam, mu, sim_time=args.sim_time, seed=args.seed, warmup=args.warmup)
    except ValueError as error:
        print(error)
        return EXIT_INVALID

    _print_single_report(lam, mu, run)
    return EXIT_OK


def _run_scenarios(args: argparse.Namespace) -> int:
    """Ejecuta los tres escenarios de la guía (múltiples réplicas por defecto).
    Genera tabla CSV/LaTeX, gráficos y muestra ruta de salida.
    """
    result = run_study(
        replications=args.replications,
        sim_time=args.sim_time,
        base_seed=DEFAULT_BASE_SEED if args.seed is None else args.seed,
        warmup=args.warmup,
    )

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    frame = comparison_dataframe(result.summaries)
    write_csv(frame, out_dir / "comparacion.csv")      # Tabla en CSV
    to_latex(frame, out_dir / "comparacion.tex")      # Tabla en LaTeX
    generate_all(result.runs, result.summaries, out_dir)  # Gráficas

    print(f"3 escenarios × {args.replications} réplicas → {out_dir}")
    return EXIT_OK


# Punto de entrada principal
def main(argv: Sequence[str] | None = None) -> int:
    """Ejecuta el programa y devuelve el código de salida.
    CLI = Línea de comandos. Decide entre modo simple o modo por escenarios.
    """
    parser = _build_parser()
    args: Any = parser.parse_args(argv)

    single = args.lam is not None or args.mu is not None
    if single and args.scenarios:
        parser.error("--scenarios no se combina con --lam/--mu")
    if single and (args.lam is None or args.mu is None):
        parser.error("el modo de una corrida necesita --lam y --mu juntos")

    if single:
        return _run_single(args)  # Una sola corrida
    return _run_scenarios(args)  # Tres escenarios de la guía
