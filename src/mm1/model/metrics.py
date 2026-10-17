"""Métricas teóricas del sistema M/M/1.

Calcula las medidas cerradas a partir de λ (llegadas) y μ (servicio).
Solo usa fórmulas, sin simulación.
"""

from __future__ import annotations

from dataclasses import dataclass

# Tolerancia absoluta para comparaciones con valores analíticos.
THEORY_TOLERANCE = 1e-9


@dataclass(frozen=True)
class TheoryMetrics:
    """Medidas teóricas del modelo M/M/1 (una cola, un servidor)."""

    rho: float  # Utilización del servidor (λ/μ)
    L: float    # Clientes promedio en el sistema
    Lq: float   # Clientes promedio en cola
    W: float    # Tiempo promedio en sistema
    Wq: float   # Tiempo promedio en cola


def utilization(lam: float, mu: float) -> float:
    """Calcula la utilización ρ = λ/μ."""
    return lam / mu


def is_stable(lam: float, mu: float) -> bool:
    """Verifica si el sistema es estable: λ < μ."""
    return lam < mu


def theoretical_metrics(lam: float, mu: float) -> TheoryMetrics:
    """Calcula las métricas teóricas para un sistema estable.
    Fórmulas (guía): L=λ/(μ-λ), Lq=λ^2/(μ(μ-λ)), W=1/(μ-λ), Wq=λ/(μ(μ-λ)), ρ=λ/μ.
    """
    if not is_stable(lam, mu):
        raise ValueError("El sistema no es estable")

    gap = mu - lam
    return TheoryMetrics(
        rho=utilization(lam, mu),
        L=lam / gap,
        Lq=lam**2 / (mu * gap),
        W=1 / gap,
        Wq=lam / (mu * gap),
    )
