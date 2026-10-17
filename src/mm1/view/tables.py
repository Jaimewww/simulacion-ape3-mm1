"""Genera la tabla comparativa entre teoría y simulación."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas

from ..model.analysis import ScenarioSummary

# Esquema de columnas de la tabla comparativa (19 columnas)
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

LATEX_CAPTION = "Comparación de resultados teóricos y simulados por escenario"
LATEX_LABEL = "tab:comparacion"
LATEX_FLOAT_FORMAT = "%.4f"


def comparison_dataframe(summaries: Sequence[ScenarioSummary]) -> pandas.DataFrame:
    """Crea un DataFrame con la comparación teoría vs simulación (ordenado por escenario).
    Columnas: valores teóricos (rho,L,Lq,W,Wq), simulados, IC95 de Wq simulado y errores relativos.
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


def write_csv(df: pandas.DataFrame, path: str | Path) -> Path:
    """Guarda la tabla en formato CSV."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)
    return destination


def to_latex(df: pandas.DataFrame, path: str | Path) -> Path:
    """Guarda la tabla en formato LaTeX para el informe."""
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
