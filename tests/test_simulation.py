"""Behaviour tests for the SimPy M/M/1 engine.

Owner: Jaime Landazuri.
Specs: S4 (guide pseudocode), S5 (per-scenario records), S6 (per-scenario metrics),
S7 (expected results).

Test-first contract for stage 3 of `CONTRIBUTING.md`: every test here fails until
`src/mm1/model/simulation.py` implements `run_mm1`.
"""

from __future__ import annotations

import statistics
from dataclasses import FrozenInstanceError
from itertools import pairwise

import pytest

from mm1.model.metrics import theoretical_metrics
from mm1.model.simulation import CustomerRecord, ScenarioRun, run_mm1

TOL = 1e-9


@pytest.fixture(scope="module")
def run() -> ScenarioRun:
    """One stable reference run reused by the read-only assertions."""
    return run_mm1(2.0, 3.0, sim_time=200.0, seed=1)


# --------------------------------------------------------------------------- #
# Stability guard (spec: Unstable input is rejected)
# --------------------------------------------------------------------------- #


def test_unstable_input_is_rejected() -> None:
    """`lam >= mu` raises ValueError and returns no ScenarioRun."""
    with pytest.raises(ValueError, match="no es estable"):
        run_mm1(3.0, 3.0)


def test_unstable_input_above_mu_is_rejected() -> None:
    """`lam > mu` is rejected with the same guide message."""
    with pytest.raises(ValueError, match="no es estable"):
        run_mm1(4.0, 3.0)


def test_non_positive_rates_are_rejected() -> None:
    """A zero or negative rate is rejected instead of crashing inside the RNG."""
    with pytest.raises(ValueError, match="positivas"):
        run_mm1(0.0, 3.0)
    with pytest.raises(ValueError, match="positivas"):
        run_mm1(2.0, -1.0)


def test_non_positive_simulation_time_is_rejected() -> None:
    """A non-positive horizon is rejected."""
    with pytest.raises(ValueError, match="sim_time"):
        run_mm1(2.0, 3.0, sim_time=0.0)


# --------------------------------------------------------------------------- #
# Single server, FIFO, one at a time (spec: Customers are served one at a time)
# --------------------------------------------------------------------------- #


def test_customers_are_served_one_at_a_time(run: ScenarioRun) -> None:
    """Each customer starts service only after the previous one has left."""
    assert run.n_customers > 0
    for previous, following in pairwise(run.customers):
        assert following.service_start >= previous.departure_time - TOL


def test_service_intervals_never_overlap(run: ScenarioRun) -> None:
    """At most one customer is in service at any instant."""
    ordered = sorted(run.customers, key=lambda c: c.service_start)
    for previous, following in pairwise(ordered):
        assert following.service_start >= previous.departure_time - TOL


def test_customers_keep_fifo_order(run: ScenarioRun) -> None:
    """Arrivals are recorded in non-decreasing arrival order with ids 0..n-1."""
    arrivals = [c.arrival_time for c in run.customers]
    assert arrivals == sorted(arrivals)
    assert [c.customer_id for c in run.customers] == list(range(run.n_customers))


# --------------------------------------------------------------------------- #
# Record identities (spec: Record invariants hold)
# --------------------------------------------------------------------------- #


def test_records_describe_each_visit(run: ScenarioRun) -> None:
    """wait/service identities and the time ordering hold for every record."""
    for customer in run.customers:
        assert customer.wait_time == pytest.approx(
            customer.service_start - customer.arrival_time, abs=TOL
        )
        assert customer.service_time == pytest.approx(
            customer.departure_time - customer.service_start, abs=TOL
        )
        assert customer.departure_time >= customer.service_start - TOL
        assert customer.service_start >= customer.arrival_time - TOL
        assert customer.wait_time >= -TOL
        assert customer.service_time > 0.0


def test_customer_records_are_frozen(run: ScenarioRun) -> None:
    """Records are immutable, so aggregation cannot corrupt the run."""
    with pytest.raises(FrozenInstanceError):
        run.customers[0].wait_time = 0.0  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# Queue trace (spec: Queue length is recorded over time)
# --------------------------------------------------------------------------- #


def test_queue_trace_is_recorded_over_time(run: ScenarioRun) -> None:
    """The trace is non-empty, monotonic in time and non-negative in length."""
    assert run.queue_trace
    times = [t for t, _ in run.queue_trace]
    lengths = [q for _, q in run.queue_trace]
    assert times == sorted(times)
    assert times[0] == 0.0
    assert all(isinstance(q, int) and q >= 0 for q in lengths)
    assert max(lengths) > 0


# --------------------------------------------------------------------------- #
# Reproducibility (spec: Same seed, same results)
# --------------------------------------------------------------------------- #


def test_same_seed_same_results() -> None:
    """Two runs with the same seed are identical, field by field."""
    first = run_mm1(2.0, 3.0, sim_time=150.0, seed=7)
    second = run_mm1(2.0, 3.0, sim_time=150.0, seed=7)
    assert first.customers == second.customers
    assert first.queue_trace == second.queue_trace
    assert first == second


def test_different_seeds_differ() -> None:
    """Different seeds produce different trajectories."""
    first = run_mm1(2.0, 3.0, sim_time=150.0, seed=7)
    second = run_mm1(2.0, 3.0, sim_time=150.0, seed=8)
    assert first.customers != second.customers


def test_seed_defaults_to_a_concrete_int() -> None:
    """`seed=None` still reports the seed it used, so a run can be replayed."""
    run = run_mm1(2.0, 3.0, sim_time=50.0)
    assert isinstance(run.seed, int)
    assert run_mm1(2.0, 3.0, sim_time=50.0, seed=run.seed) == run


# --------------------------------------------------------------------------- #
# Warmup (spec: Warmup excludes early customers from the statistics)
# --------------------------------------------------------------------------- #


def test_warmup_excludes_early_customers() -> None:
    """Statistics use only customers arriving after warmup; records keep all."""
    warmup, sim_time = 20.0, 200.0
    run = run_mm1(2.0, 3.0, sim_time=sim_time, seed=3, warmup=warmup)

    assert run.warmup == warmup
    assert run.n_customers == len(run.customers)
    assert any(c.arrival_time < warmup for c in run.customers)

    kept = [c for c in run.customers if c.arrival_time >= warmup]
    assert kept
    assert run.mean_wait == pytest.approx(
        sum(c.wait_time for c in kept) / len(kept), abs=TOL
    )
    assert run.mean_system_time == pytest.approx(
        sum(c.departure_time - c.arrival_time for c in kept) / len(kept), abs=TOL
    )


# --------------------------------------------------------------------------- #
# Horizon and reported statistics
# --------------------------------------------------------------------------- #


def test_sim_time_bounds_the_run(run: ScenarioRun) -> None:
    """No customer arrives or departs after the simulated horizon."""
    for customer in run.customers:
        assert customer.arrival_time < run.sim_time
        assert customer.departure_time <= run.sim_time + TOL


def test_run_echoes_its_parameters() -> None:
    """The result carries the parameters it was called with."""
    run = run_mm1(2.5, 3.0, sim_time=120.0, seed=11, scenario=2, warmup=10.0)
    assert (run.lam, run.mu, run.scenario) == (2.5, 3.0, 2)
    assert (run.sim_time, run.warmup, run.seed) == (120.0, 10.0, 11)


def test_statistics_are_coherent(run: ScenarioRun) -> None:
    """Mean system time is wait plus service, and the system holds the queue."""
    mean_service = sum(c.service_time for c in run.customers) / run.n_customers
    assert run.mean_system_time == pytest.approx(run.mean_wait + mean_service, abs=1e-6)
    assert run.mean_in_system >= run.mean_queue - TOL
    assert 0.0 <= run.utilization <= 1.0
    assert run.mean_wait >= 0.0
    assert run.mean_queue >= 0.0


def test_capacity_is_one_server(run: ScenarioRun) -> None:
    """Utilization stays bounded by one server and grows with the load."""
    light = run_mm1(1.0, 3.0, sim_time=400.0, seed=5)
    heavy = run_mm1(2.9, 3.0, sim_time=400.0, seed=5)
    assert heavy.utilization > light.utilization
    assert heavy.mean_queue > light.mean_queue


def test_empty_run_is_valid() -> None:
    """A horizon shorter than the first inter-arrival time yields an empty run."""
    run = run_mm1(0.01, 3.0, sim_time=1.0, seed=1)
    assert isinstance(run, ScenarioRun)
    assert run.n_customers == 0
    assert run.customers == ()
    assert run.mean_wait == 0.0
    assert run.utilization == 0.0


def test_customer_record_fields_are_floats(run: ScenarioRun) -> None:
    """Records expose floats, no numpy scalars leaking into the public type."""
    record = run.customers[0]
    assert isinstance(record, CustomerRecord)
    for value in (record.arrival_time, record.service_start, record.departure_time):
        assert isinstance(value, float)


# --------------------------------------------------------------------------- #
# Oracle tie-in (design.md: metrics.py is the correctness oracle)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("lam", [2.0, 2.5])
def test_single_run_tracks_the_theory(lam: float) -> None:
    """One long run lands within 15% of the analytic queue metrics."""
    result = run_mm1(lam, 3.0, sim_time=2000.0, seed=42)
    theory = theoretical_metrics(lam, 3.0)
    assert abs(result.mean_wait - theory.Wq) / theory.Wq < 0.15
    assert abs(result.mean_queue - theory.Lq) / theory.Lq < 0.15


def test_replicas_converge_to_the_theory_at_high_utilization() -> None:
    """At rho = 0.967 the mean over replicas lands near theory; one run cannot.

    This is the quantitative answer to guide section 7 question 9: as rho
    approaches 1 the waiting time gets a heavy tail, so a single run is not
    evidence of anything. Averaging replicas is what makes the theory-vs-
    simulation table defensible, which is why the plan requires 30 of them.
    """
    theory = theoretical_metrics(2.9, 3.0)
    waits = [run_mm1(2.9, 3.0, sim_time=2000.0, seed=s).mean_wait for s in range(12)]
    mean_wait = statistics.fmean(waits)

    assert abs(mean_wait - theory.Wq) / theory.Wq < 0.20
    assert statistics.stdev(waits) > 0.10 * mean_wait
