"""SimPy M/M/1 simulation core.

Owner: Jaime Landazuri.
Specs: S4 (pseudocode), S5 (scenarios), S6 (per-scenario records).

This module defines the data recorded by one simulation run and the entry point
that drives the discrete-event model described in guide section 5.1: one Poisson
arrival stream, one server of ``capacity = 1``, exponential service times and a
FIFO queue.

Decisions documented here because they are visible in the results:

* The random numbers come from the standard-library ``random.Random`` seeded per
  run, not from a global generator, so a run is reproducible from ``seed`` alone
  on any interpreter version.
* ``queue_trace`` is piecewise constant: each ``(time, length)`` entry holds from
  its own time until the next entry. The timer averages over that trace.
* A customer whose service would finish after ``sim_time`` still occupies the
  server until the horizon but is **not** recorded, so every recorded visit is a
  completed one and ``departure_time <= sim_time`` always holds. This is the
  usual end-of-horizon truncation; its bias is negligible for the 1000-unit runs
  the practice uses and it is why ``n_customers`` means "completed visits".
* Input is validated before the model runs: non-positive rates, a non-positive
  horizon and an out-of-range ``warmup`` are rejected with a diagnostic message,
  while ``lam >= mu`` raises the guide's own ``El sistema no es estable``.
"""

from __future__ import annotations

import random
from collections.abc import Generator
from dataclasses import dataclass

import simpy

from .metrics import is_stable

# Upper bound for the seed drawn when the caller passes ``seed=None``.
_MAX_SEED = 2**32


# SPEC: S4, S6 — one simulated customer and its wait/service times.
@dataclass(frozen=True)
class CustomerRecord:
    """Timeline of a single simulated customer.

    Attributes:
        customer_id: Sequential identifier of the customer.
        arrival_time: Simulation time at which the customer arrives.
        service_start: Simulation time at which service starts.
        departure_time: Simulation time at which the customer leaves.
        wait_time: Time spent waiting in the queue.
        service_time: Time spent being served.
    """

    customer_id: int
    arrival_time: float
    service_start: float
    departure_time: float
    wait_time: float
    service_time: float


# SPEC: S4, S6 — aggregate result of one scenario run.
@dataclass(frozen=True)
class ScenarioRun:
    """Aggregated result of a single M/M/1 simulation run.

    Attributes:
        scenario: Scenario identifier the run belongs to.
        lam: Arrival rate used in the run.
        mu: Service rate used in the run.
        seed: Random seed used in the run.
        sim_time: Total simulated time.
        warmup: Warm-up period discarded from statistics.
        n_customers: Number of customers that completed service.
        mean_wait: Simulated average waiting time in the queue.
        mean_queue: Simulated average queue length.
        mean_system_time: Simulated average time in the system.
        mean_in_system: Simulated average number of customers in the system.
        utilization: Simulated server utilization.
        customers: Per-customer records of the run.
        queue_trace: Sampled ``(time, queue_length)`` pairs.
    """

    scenario: int
    lam: float
    mu: float
    seed: int
    sim_time: float
    warmup: float
    n_customers: int
    mean_wait: float
    mean_queue: float
    mean_system_time: float
    mean_in_system: float
    utilization: float
    customers: tuple[CustomerRecord, ...]
    queue_trace: tuple[tuple[float, int], ...]


# SPEC: S4 — reject input that cannot produce a stationary M/M/1 result.
def _validate(lam: float, mu: float, sim_time: float, warmup: float) -> None:
    """Reject parameters the model cannot use.

    Args:
        lam: Arrival rate ``lambda``.
        mu: Service rate ``mu``.
        sim_time: Total simulated time.
        warmup: Warm-up period.

    Raises:
        ValueError: If a rate is not positive, if the horizon is not positive, if
            ``warmup`` falls outside ``[0, sim_time)``, or if ``lam >= mu``.
    """
    if lam <= 0 or mu <= 0:
        raise ValueError("las tasas lam y mu deben ser positivas")
    if sim_time <= 0:
        raise ValueError("sim_time debe ser mayor que 0")
    if warmup < 0 or warmup >= sim_time:
        raise ValueError("warmup debe cumplir 0 <= warmup < sim_time")
    if not is_stable(lam, mu):
        raise ValueError("El sistema no es estable")


# SPEC: S4 — spawn customers with exponential inter-arrival times.
def _arrivals(
    env: simpy.Environment,
    server: simpy.Resource,
    rng: random.Random,
    lam: float,
    mu: float,
    sim_time: float,
    customers: list[CustomerRecord],
    queue_trace: list[tuple[float, int]],
) -> Generator[simpy.Event, None, None]:
    """Generate arrivals until the horizon and start one process per customer."""
    customer_id = 0
    while True:
        yield env.timeout(rng.expovariate(lam))
        if env.now >= sim_time:
            return
        env.process(
            _customer(
                env,
                server,
                rng,
                mu,
                sim_time,
                customer_id,
                float(env.now),
                customers,
                queue_trace,
            )
        )
        customer_id += 1


# SPEC: S4, S6 — queue for the single server, then serve FIFO.
def _customer(
    env: simpy.Environment,
    server: simpy.Resource,
    rng: random.Random,
    mu: float,
    sim_time: float,
    customer_id: int,
    arrival_time: float,
    customers: list[CustomerRecord],
    queue_trace: list[tuple[float, int]],
) -> Generator[simpy.Event, None, None]:
    """Request the server, record the visit if it completes inside the horizon."""
    with server.request() as request:
        queue_trace.append((float(env.now), len(server.queue)))
        yield request

        service_start = float(env.now)
        queue_trace.append((service_start, len(server.queue)))

        service_time = rng.expovariate(mu)
        departure_time = service_start + service_time
        if departure_time > sim_time:
            # In service at the horizon: keep the server busy, record nothing.
            yield env.timeout(max(sim_time - service_start, 0.0))
            return

        yield env.timeout(service_time)
        customers.append(
            CustomerRecord(
                customer_id=customer_id,
                arrival_time=arrival_time,
                service_start=service_start,
                departure_time=departure_time,
                wait_time=service_start - arrival_time,
                service_time=service_time,
            )
        )


# SPEC: S6 — value of a piecewise-constant function at one instant.
def _value_at(breakpoints: list[tuple[float, float]], when: float) -> float:
    """Return the last value whose time is ``<= when``, or ``0.0`` before the first."""
    value = 0.0
    for time, candidate in breakpoints:
        if time > when:
            break
        value = candidate
    return value


# SPEC: S6 — time average of a piecewise-constant function over a window.
def _time_average(
    breakpoints: list[tuple[float, float]], start: float, end: float
) -> float:
    """Average a piecewise-constant function over ``[start, end]``.

    Args:
        breakpoints: ``(time, value)`` pairs sorted by time; each value holds from
            its own time until the next entry.
        start: Left edge of the observation window.
        end: Right edge of the observation window.

    Returns:
        The time-weighted average, or ``0.0`` for an empty window.
    """
    if end <= start:
        return 0.0

    total = 0.0
    cursor = start
    current = _value_at(breakpoints, start)
    for time, value in breakpoints:
        if time <= start:
            continue
        if time >= end:
            break
        total += current * (time - cursor)
        cursor, current = time, value
    total += current * (end - cursor)
    return total / (end - start)


# SPEC: S6 — number of customers inside the system over time.
def _in_system_breakpoints(customers: list[CustomerRecord]) -> list[tuple[float, float]]:
    """Build the piecewise-constant customer count inside the system."""
    events: list[tuple[float, float]] = []
    for customer in customers:
        events.append((customer.arrival_time, 1.0))
        events.append((customer.departure_time, -1.0))
    events.sort(key=lambda event: event[0])

    breakpoints: list[tuple[float, float]] = []
    inside = 0.0
    for time, delta in events:
        inside += delta
        breakpoints.append((time, inside))
    return breakpoints


# SPEC: S4, S5 — run one M/M/1 scenario with SimPy.
def run_mm1(
    lam: float,
    mu: float,
    sim_time: float = 1000.0,
    seed: int | None = None,
    scenario: int = 0,
    warmup: float = 0.0,
) -> ScenarioRun:
    """Simulate one M/M/1 scenario and return its aggregated result.

    Args:
        lam: Average arrival rate ``lambda``.
        mu: Average service rate ``mu``.
        sim_time: Total simulated time in the same time units as the rates.
        seed: Optional seed for the random number generator. When omitted, a seed
            is drawn and reported in the result so the run can be replayed.
        scenario: Scenario identifier attached to the result.
        warmup: Warm-up period discarded from the reported statistics. Customer
            records keep the whole run; only the statistics are filtered.

    Returns:
        The :class:`ScenarioRun` produced by the simulation.

    Raises:
        ValueError: If the parameters are unusable, or if ``lam >= mu``.
    """
    _validate(lam, mu, sim_time, warmup)

    resolved_seed = seed if seed is not None else random.Random().randrange(_MAX_SEED)
    rng = random.Random(resolved_seed)

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=1)
    customers: list[CustomerRecord] = []
    queue_trace: list[tuple[float, int]] = [(0.0, 0)]

    env.process(_arrivals(env, server, rng, lam, mu, sim_time, customers, queue_trace))
    env.run(until=sim_time)

    window = sim_time - warmup
    counted = [customer for customer in customers if customer.arrival_time >= warmup]
    completed = len(customers)

    if counted:
        mean_wait = sum(c.wait_time for c in counted) / len(counted)
        mean_system_time = sum(
            c.departure_time - c.arrival_time for c in counted
        ) / len(counted)
    else:
        mean_wait = 0.0
        mean_system_time = 0.0

    busy = 0.0
    for customer in customers:
        start = max(customer.service_start, warmup)
        stop = min(customer.departure_time, sim_time)
        if stop > start:
            busy += stop - start

    trace = [(float(time), float(length)) for time, length in queue_trace]
    return ScenarioRun(
        scenario=scenario,
        lam=lam,
        mu=mu,
        seed=resolved_seed,
        sim_time=sim_time,
        warmup=warmup,
        n_customers=completed,
        mean_wait=mean_wait,
        mean_queue=_time_average(trace, warmup, sim_time),
        mean_system_time=mean_system_time,
        mean_in_system=_time_average(_in_system_breakpoints(customers), warmup, sim_time),
        utilization=busy / window,
        customers=tuple(customers),
        queue_trace=tuple(queue_trace),
    )
