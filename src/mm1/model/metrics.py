"""Theoretical metrics of the M/M/1 queue.

Owner: Richard Chamba.
Specs: S3 (theoretical model and formulas), S6 (per-scenario metrics).

This module holds the closed-form measures of the M/M/1 system. It contains no
randomness, no SimPy and no I/O: only the analytical definitions frozen by the
guide (`docs/guia/ape3_guia_simulacion_semana3.txt`, section 5.1).
"""

from __future__ import annotations

from dataclasses import dataclass

# Absolute tolerance for comparisons with analytic values, never for stability.
THEORY_TOLERANCE = 1e-9


# SPEC: S3 — theoretical measures listed in guide section 5.1.
@dataclass(frozen=True)
class TheoryMetrics:
    """Theoretical performance measures of an M/M/1 queue.

    Attributes:
        rho: Server utilization ``lambda / mu``.
        L: Average number of customers in the system.
        Lq: Average number of customers waiting in the queue.
        W: Average time a customer spends in the system.
        Wq: Average time a customer spends waiting in the queue.
    """

    rho: float
    L: float
    Lq: float
    W: float
    Wq: float


# SPEC: S3 — server utilization rho = lambda / mu.
def utilization(lam: float, mu: float) -> float:
    """Return the server utilization ``rho = lam / mu``.

    Args:
        lam: Average arrival rate ``lambda``.
        mu: Average service rate ``mu``.

    Returns:
        The utilization of the single server.
    """
    return lam / mu


# SPEC: S3 — the system is stable when lambda < mu.
def is_stable(lam: float, mu: float) -> bool:
    """Return whether the queue is stable, i.e. ``lam < mu``.

    Args:
        lam: Average arrival rate ``lambda``.
        mu: Average service rate ``mu``.

    Returns:
        ``True`` when the stability condition ``lambda < mu`` holds.
    """
    return lam < mu


# SPEC: S3, S6 — rho, L, Lq, W and Wq for a stable system.
def theoretical_metrics(lam: float, mu: float) -> TheoryMetrics:
    """Return the theoretical ``rho``, ``L``, ``Lq``, ``W`` and ``Wq``.

    Args:
        lam: Average arrival rate ``lambda``.
        mu: Average service rate ``mu``.

    Returns:
        The :class:`TheoryMetrics` for a stable system.

    Raises:
        ValueError: If ``lam >= mu``; stationary metrics do not exist.
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
