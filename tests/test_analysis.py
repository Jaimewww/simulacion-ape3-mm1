"""Replication analysis against independently computed fixtures (4.3–4.5)."""

from dataclasses import FrozenInstanceError, replace
from math import pi, tan

import pytest

from mm1.model.analysis import confidence_interval, relative_error, summarize
from mm1.model.metrics import theoretical_metrics
from mm1.model.scenarios import run_scenarios
from mm1.model.simulation import ScenarioRun


@pytest.fixture
def runs() -> list[ScenarioRun]:
    return [
        ScenarioRun(
            scenario=1,
            lam=2.0,
            mu=3.0,
            seed=i,
            sim_time=100.0,
            warmup=0.0,
            n_customers=10 * i,
            mean_wait=float(i),
            mean_queue=2.0 * i,
            mean_system_time=i + 1.0,
            mean_in_system=3.0 * i,
            utilization=0.2 * i,
            customers=(),
            queue_trace=(),
        )
        for i in (1, 2, 3)
    ]


def test_confidence_interval_spec_example() -> None:
    assert confidence_interval([1.0, 2.0, 3.0]) == pytest.approx((-0.4841, 4.4841), abs=1e-4)


# Task 4.3 oracle, preserved at the five decimals printed in the plan.
T95 = [
    value
    for row in (
        (12.70620, 4.30265, 3.18245, 2.77645, 2.57058, 2.44691, 2.36462, 2.30600, 2.26216, 2.22814),
        (2.20099, 2.17881, 2.16037, 2.14479, 2.13145, 2.11991, 2.10982, 2.10092, 2.09302, 2.08596),
        (2.07961, 2.07387, 2.06866, 2.06390, 2.05954, 2.05553, 2.05183, 2.04841, 2.04523, 2.04227),
    )
    for value in row
]


@pytest.mark.parametrize(("df", "critical"), tuple(enumerate(T95, start=1)))
def test_student_t_quantile_oracle(df: int, critical: float) -> None:
    # For this sample, mean=1/n and sample standard error=1/n.
    low, high = confidence_interval([0.0] * df + [1.0])
    # The plan's table is rounded to five decimals.
    assert (high - low) * (df + 1) / 2 == pytest.approx(critical, rel=0, abs=5e-6)


@pytest.mark.parametrize("confidence", [0.1, 0.5, 0.8, 0.9, 0.99, 0.999])
def test_other_confidence_levels_against_cauchy_quantile(confidence: float) -> None:
    # Student-t with one degree of freedom is the standard Cauchy distribution.
    critical = tan(pi * confidence / 2)
    assert confidence_interval([0.0, 2.0], confidence) == pytest.approx(
        (1 - critical, 1 + critical), rel=1e-9, abs=1e-9
    )


def test_large_sample_approaches_normal_limit() -> None:
    n = 100_001
    low, high = confidence_interval([0.0] * (n - 1) + [1.0])
    assert (high - low) * n / 2 == pytest.approx(1.95996, abs=3e-5)


def test_interval_singleton_and_constant_samples() -> None:
    assert confidence_interval([7.0]) == (7.0, 7.0)
    assert confidence_interval([7.0, 7.0, 7.0]) == (7.0, 7.0)


@pytest.mark.parametrize("values", [[], [float("nan")], [1.0, float("inf")]])
def test_invalid_samples_are_rejected(values) -> None:
    with pytest.raises(ValueError):
        confidence_interval(values)


@pytest.mark.parametrize("confidence", [0, 1, -0.1, 1.1, float("nan")])
def test_invalid_confidence_is_rejected(confidence: float) -> None:
    with pytest.raises(ValueError):
        confidence_interval([7.0], confidence)


@pytest.mark.parametrize(
    ("simulated", "theoretical", "expected"),
    [(1.05, 1.0, 0.05), (0.0, 1.0, 1.0), (1.0, 2.0, 0.5), (1.0, -2.0, 1.5)],
)
def test_relative_error(simulated: float, theoretical: float, expected: float) -> None:
    assert relative_error(simulated, theoretical) == pytest.approx(expected)


def test_zero_theory_error_policy() -> None:
    for simulated in (0.0, 1.0):
        with pytest.raises(ValueError, match="zero"):
            relative_error(simulated, 0.0)


def test_summary_means_deviation_errors_and_immutability(runs) -> None:
    (summary,) = summarize(runs)
    assert (summary.scenario, summary.lam, summary.mu, summary.replications) == (1, 2.0, 3.0, 3)
    assert summary.theory == theoretical_metrics(2.0, 3.0)
    assert (summary.sim_mean_wait, summary.sim_mean_queue, summary.sim_mean_in_system) == (2, 4, 6)
    assert summary.sim_utilization == pytest.approx(0.4)
    assert summary.std_wait == 1.0  # Sample standard deviation, ddof=1.
    assert summary.ci95_wait == confidence_interval([1.0, 2.0, 3.0])
    assert (summary.rel_error_L, summary.rel_error_Lq) == pytest.approx((2, 2))
    assert (summary.rel_error_W, summary.rel_error_Wq) == pytest.approx((2, 2))
    with pytest.raises(FrozenInstanceError):
        summary.std_wait = 0.0


def test_grouping_is_sorted_and_does_not_mix_scenarios(runs) -> None:
    other = replace(runs[0], scenario=3, lam=2.9)
    summaries = summarize([other, *reversed(runs)])
    assert [s.scenario for s in summaries] == [1, 3]
    assert [s.replications for s in summaries] == [3, 1]
    assert summaries[1].sim_mean_wait == 1.0
    assert summaries[1].std_wait == 0.0
    assert summaries[1].ci95_wait == (1.0, 1.0)


def test_empty_summary_is_rejected() -> None:
    with pytest.raises(ValueError):
        summarize([])


def test_inconsistent_rates_within_scenario_are_rejected(runs) -> None:
    with pytest.raises(ValueError, match="rates"):
        summarize([runs[0], replace(runs[1], lam=2.5)])


def test_scenario_analysis_integration() -> None:
    runs = run_scenarios(3, 100.0)
    summaries = summarize(runs)
    assert [s.scenario for s in summaries] == [1, 2, 3]
    for summary in summaries:
        peers = [r for r in runs if r.scenario == summary.scenario]
        assert summary.replications == 3
        assert summary.theory == theoretical_metrics(summary.lam, summary.mu)
        assert summary.sim_mean_wait == pytest.approx(sum(r.mean_wait for r in peers) / 3)
        assert summary.ci95_wait[0] <= summary.sim_mean_wait <= summary.ci95_wait[1]


def test_preserve_default_confidence_is_95_percent() -> None:
    values = [1.0, 2.0, 3.0]
    assert confidence_interval(values) == confidence_interval(values, confidence=0.95)
