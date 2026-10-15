"""Analytic oracle tests for Richard Chamba's theory stage (S3)."""

from dataclasses import FrozenInstanceError, astuple

import pytest

from mm1.model.metrics import (
    THEORY_TOLERANCE,
    is_stable,
    theoretical_metrics,
    utilization,
)


@pytest.mark.parametrize(
    ("lam", "expected"),
    [
        (2.0, (2 / 3, 2.0, 4 / 3, 1.0, 2 / 3)),
        (2.5, (5 / 6, 5.0, 25 / 6, 2.0, 5 / 3)),
        (2.9, (29 / 30, 29.0, 841 / 30, 10.0, 29 / 3)),
    ],
)
def test_guide_scenarios(lam: float, expected: tuple[float, ...]) -> None:
    metrics = theoretical_metrics(lam, 3.0)
    assert astuple(metrics) == pytest.approx(expected, rel=0, abs=THEORY_TOLERANCE)
    assert utilization(lam, 3.0) == pytest.approx(expected[0], rel=0, abs=THEORY_TOLERANCE)
    assert metrics.rho < 1


@pytest.mark.parametrize(
    ("lam", "expected"), [(2.0, True), (2.9, True), (3.0, False), (3.1, False)]
)
def test_stability_boundary(lam: float, expected: bool) -> None:
    assert is_stable(lam, 3.0) is expected


@pytest.mark.parametrize("lam", [3.0, 3.1])
def test_unstable_metrics_are_rejected(lam: float) -> None:
    with pytest.raises(ValueError, match="El sistema no es estable"):
        theoretical_metrics(lam, 3.0)


def test_metrics_are_immutable() -> None:
    metrics = theoretical_metrics(2.0, 3.0)
    with pytest.raises(FrozenInstanceError):
        metrics.L = 100.0


@pytest.mark.parametrize("lam", [2.0, 2.5, 2.9])
def test_queue_and_system_identities(lam: float) -> None:
    metrics = theoretical_metrics(lam, 3.0)
    assert metrics.Lq == pytest.approx(metrics.L - metrics.rho, rel=0, abs=THEORY_TOLERANCE)
    assert metrics.Wq == pytest.approx(metrics.W - 1 / 3.0, rel=0, abs=THEORY_TOLERANCE)
    assert metrics.L == pytest.approx(lam * metrics.W, rel=0, abs=THEORY_TOLERANCE)
    assert metrics.Lq == pytest.approx(lam * metrics.Wq, rel=0, abs=THEORY_TOLERANCE)


def test_preserve_mean_in_system_formula() -> None:
    lam, mu = 1.2, 4.0
    assert theoretical_metrics(lam, mu).L == lam / (mu - lam)


def test_preserve_mean_system_time_formula() -> None:
    lam, mu = 1.2, 4.0
    assert theoretical_metrics(lam, mu).W == 1 / (mu - lam)


def test_preserve_near_saturation_stability() -> None:
    assert is_stable(2.9, 3.0) is True


def test_stability_uses_strict_comparison_without_rounding() -> None:
    assert is_stable(3.0 - 1e-12, 3.0) is True
    assert is_stable(3.0 + 1e-12, 3.0) is False
