# Delta for mm1-simulation

## ADDED Requirements

### Requirement: The simulator MUST implement the guide M/M/1 procedure

`run_mm1(lam, mu, sim_time=1000.0, seed=None, scenario=0, warmup=0.0)` MUST create
a SimPy environment with exactly one server of `capacity = 1`, generate customers
with exponential inter-arrival times of rate `lam`, serve them FIFO with
exponential service times of rate `mu`, release the server after each service, and
return a `ScenarioRun`. Unstable input (`lam >= mu`) MUST raise `ValueError`.
Specs: S4, S7.

#### Scenario: Customers are served one at a time

- GIVEN `lam = 2.0`, `mu = 3.0`, `sim_time = 200.0`, `seed = 1`
- WHEN `run_mm1` completes
- THEN `n_customers > 0`
- AND for every pair of consecutive `CustomerRecord`s in FIFO order the later
  customer's `service_start` is greater than or equal to the earlier customer's
  `departure_time`

#### Scenario: Queue length is recorded over time

- GIVEN any stable run
- THEN `queue_trace` is a non-empty tuple of `(time, queue_length)` pairs
- AND times are non-decreasing, queue lengths are non-negative integers
- AND at most one customer is in service at any instant

#### Scenario: Unstable input is rejected

- GIVEN `lam = 3.0`, `mu = 3.0`
- WHEN `run_mm1(3.0, 3.0)` is called
- THEN it raises `ValueError` mentioning instability
- AND no `ScenarioRun` is returned

### Requirement: Customer records MUST describe each visit

Each customer MUST produce a frozen `CustomerRecord(customer_id, arrival_time,
service_start, departure_time, wait_time, service_time)` where
`wait_time == service_start - arrival_time`, `service_time == departure_time -
service_start`, and `departure_time >= service_start >= arrival_time`.
Specs: S4, S6, S7.

#### Scenario: Record invariants hold

- GIVEN a completed stable run
- WHEN each `CustomerRecord` is inspected
- THEN the ordering, wait-time and service-time identities hold within `1e-9`

### Requirement: Simulation statistics MUST be reproducible and observable

Each `ScenarioRun` MUST expose `scenario`, `lam`, `mu`, `seed`, `sim_time`,
`warmup`, `n_customers`, `mean_wait`, `mean_queue`, `mean_system_time`,
`mean_in_system`, `utilization`, the `customers` tuple and the `queue_trace`.
The same `seed` MUST yield identical customer records and statistics. Statistics
MUST be computed only from customers with `arrival_time >= warmup`, while
`customers` and `n_customers` keep the full run. Specs: S6, S7.

#### Scenario: Same seed, same results

- GIVEN two calls to `run_mm1(2.0, 3.0, sim_time=150.0, seed=7)`
- WHEN both runs complete
- THEN their `customers`, `mean_wait`, `mean_queue`, `mean_system_time`,
  `mean_in_system` and `utilization` are equal

#### Scenario: Warmup excludes early customers from the statistics

- GIVEN `warmup = 20.0` and `sim_time = 200.0`
- WHEN the run completes
- THEN `warmup` is echoed in the result
- AND every statistic equals the statistic recomputed from the records whose
  `arrival_time >= 20.0`
- AND `n_customers` still counts every recorded customer

### Requirement: The three guide scenarios SHALL be declared as data

`SCENARIOS` MUST be a tuple of exactly three frozen `Scenario` entries with
`id` 1..3, `lam`/`mu` = `(2.0, 3.0)`, `(2.5, 3.0)`, `(2.9, 3.0)`, labels matching
the guide table, and conditions `Sistema estable`, `Mayor utilización`,
`Cerca de saturación`. Spec: S5.

#### Scenario: Scenario table matches the guide

- GIVEN `SCENARIOS` is imported
- THEN `[(s.id, s.lam, s.mu) for s in SCENARIOS] == [(1, 2.0, 3.0), (2, 2.5, 3.0), (3, 2.9, 3.0)]`
- AND every entry has a non-empty `label` and `condition`
- AND `is_stable(s.lam, s.mu)` is `True` for all three

### Requirement: Replicated runs MUST be groupable per scenario

`run_scenarios(replications=30, sim_time=1000.0, base_seed=42, warmup=0.0)` MUST
return `replications * 3` `ScenarioRun` objects. Seeds MUST be derived
deterministically from `base_seed` and the `(scenario, replication)` pair, so two
identical calls return identical results. Every run MUST carry its scenario id so
`analysis.summarize` can group it. Specs: S6, S7.

#### Scenario: Expected run count and grouping

- GIVEN `replications = 3`
- WHEN `run_scenarios(replications=3, sim_time=100.0)` is called
- THEN 9 runs are returned
- AND the scenario ids are `1, 1, 1, 2, 2, 2, 3, 3, 3` in order

#### Scenario: Deterministic replication seeds

- GIVEN two identical `run_scenarios` calls with the same `base_seed`
- THEN the per-run `seed` values and `mean_wait` values are equal pairwise
