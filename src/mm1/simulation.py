"""SimPy M/M/1 simulation core.

Owner: Jaime Landazuri.
Specs: S4 (pseudocode), S5 (scenarios), S6 (per-scenario records).

This module defines the data recorded by one simulation run and the entry point
that drives the discrete-event model described in guide section 5.1.
"""

from __future__ import annotations

from dataclasses import dataclass


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
        seed: Optional seed for the random number generator.
        scenario: Scenario identifier attached to the result.
        warmup: Warm-up period discarded from the reported statistics.

    Returns:
        The :class:`ScenarioRun` produced by the simulation.
    """
    raise NotImplementedError("Jaime Landazuri — see openspec plan")
