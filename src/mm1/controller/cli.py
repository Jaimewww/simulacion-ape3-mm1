"""Command-line entry point for the M/M/1 practice.

Owner: Jaime Landazuri.
Specs: S4 (pseudocode workflow), S6 (per-scenario metrics), S14 (agent-executable
entry point).

The command has two modes:

* **single run** — ``--lam`` and ``--mu`` run one simulation and print the
  simulated metrics next to the theoretical ones. This is the live probe used
  during the oral defense and the only mode that needs nothing but the engine.
* **the guide's three scenarios** — ``--scenarios`` (the default when no rates
  are given) runs the whole study through ``controller.study.run_study`` and
  writes the comparison table and the figures into ``--out``. It exists so the
  CLI has exactly one orchestration path, the same one the Streamlit page uses.

The console report is deliberately plain text: the printable comparison table
and the figures belong to ``mm1.view``.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from ..model.metrics import is_stable, theoretical_metrics
from ..model.simulation import ScenarioRun, run_mm1
from ..view import comparison_dataframe, generate_all, write_csv
from .study import run_study

DEFAULT_OUTPUT_DIR = Path("outputs")
DEFAULT_BASE_SEED = 42
EXIT_OK = 0
EXIT_UNSTABLE = 2
EXIT_INVALID = 3


# SPEC: S4, S14 — the flag surface frozen in design.md.
def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with the frozen flag surface."""
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
        help="tasa de llegada λ del modo de una corrida",
    )
    parser.add_argument(
        "--mu",
        type=float,
        default=None,
        metavar="MU",
        help="tasa de servicio μ del modo de una corrida",
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
        help="semilla; en modo multi-escenario es la semilla base",
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
        help="directorio de salida del modo multi-escenario (por defecto outputs)",
    )
    return parser


# SPEC: S4, S6 — print the simulated metrics next to the theoretical ones.
def _print_single_report(lam: float, mu: float, run: ScenarioRun) -> None:
    """Print one run's simulated metrics against the analytical oracle."""
    theory = theoretical_metrics(lam, mu)
    print(f"Corrida única M/M/1   λ={lam:g}  μ={mu:g}  ρ_teórica={theory.rho:.4f}")
    print(f"{'métrica':<14}{'teórica':>12}{'simulada':>12}{'error rel.':>12}")
    for label, expected, observed in (
        ("Wq", theory.Wq, run.mean_wait),
        ("W", theory.W, run.mean_system_time),
        ("Lq", theory.Lq, run.mean_queue),
        ("L", theory.L, run.mean_in_system),
        ("utilización", theory.rho, run.utilization),
    ):
        error = abs(observed - expected) / expected if expected else 0.0
        print(f"{label:<14}{expected:>12.4f}{observed:>12.4f}{error:>11.2%}")
    print(
        f"clientes atendidos={run.n_customers}  sim_time={run.sim_time:g}"
        f"  warmup={run.warmup:g}  semilla={run.seed}"
    )


# SPEC: S4 — one simulation driven straight from the command line.
def _run_single(args: argparse.Namespace) -> int:
    """Run one simulation and report it. Writes no files."""
    lam: float = args.lam
    mu: float = args.mu
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


# SPEC: S4, S6, S7 — the guide's three scenarios, through the shared service.
def _run_scenarios(args: argparse.Namespace) -> int:
    """Run the three-scenario study and export its table and figures."""
    result = run_study(
        replications=args.replications,
        sim_time=args.sim_time,
        base_seed=DEFAULT_BASE_SEED if args.seed is None else args.seed,
        warmup=args.warmup,
    )

    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(comparison_dataframe(result.summaries), out_dir / "comparacion.csv")
    generate_all(result.runs, result.summaries, out_dir)

    print(f"3 escenarios × {args.replications} réplicas → {out_dir}")
    return EXIT_OK


# SPEC: S4, S14 — run the end-to-end workflow from the command line.
def main(argv: Sequence[str] | None = None) -> int:
    """Run the M/M/1 workflow and return a process exit code.

    Args:
        argv: Command-line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        The process exit code: ``0`` on success, ``2`` when the requested system
        is unstable, ``3`` when the parameters are unusable. argparse exits with
        ``2`` on a usage error, and ``--help`` exits with ``0``.
    """
    parser = _build_parser()
    args: Any = parser.parse_args(argv)

    single = args.lam is not None or args.mu is not None
    if single and args.scenarios:
        parser.error("--scenarios no se combina con --lam/--mu")
    if single and (args.lam is None or args.mu is None):
        parser.error("el modo de una corrida necesita --lam y --mu juntos")

    if single:
        return _run_single(args)
    return _run_scenarios(args)
