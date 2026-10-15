# Delta for mm1-theory

## ADDED Requirements

### Requirement: Server utilization MUST use rho = lambda / mu

The system MUST compute server utilization as `rho = lambda / mu`.

Guide §5.1 prints `rho = mu / lambda`, which contradicts the guide's own
stability condition `lambda < mu` and the textbook M/M/1 definition. The
implementation MUST follow `rho = lambda / mu` and the deviation MUST be
documented as decision D1 in `design.md` and in the technical document. Spec: S3.

#### Scenario: Utilization for scenario 1

- GIVEN `lam = 2.0` and `mu = 3.0`
- WHEN `utilization(2.0, 3.0)` is called
- THEN it returns `0.666666...` (within `1e-9`)
- AND the result is strictly less than 1

#### Scenario: Utilization for near-saturation scenario 3

- GIVEN `lam = 2.9` and `mu = 3.0`
- WHEN `utilization(2.9, 3.0)` is called
- THEN it returns `0.966666...` (within `1e-9`)
- AND `is_stable(2.9, 3.0)` returns `True`

### Requirement: Stability check MUST reject lambda >= mu

The system MUST expose `is_stable(lam, mu) -> bool` that returns `False` when
`lam >= mu`, and the CLI MUST print exactly `El sistema no es estable` for that
case, matching the guide pseudocode `SI λ >= μ`. Specs: S3, S4.

#### Scenario: Equal rates are unstable

- GIVEN `lam = 3.0` and `mu = 3.0`
- WHEN `is_stable(3.0, 3.0)` is called
- THEN it returns `False`

#### Scenario: Stable rates are accepted

- GIVEN `lam = 2.0` and `mu = 3.0`
- WHEN `is_stable(2.0, 3.0)` is called
- THEN it returns `True`

### Requirement: Theoretical metrics MUST follow the guide formulas

`theoretical_metrics(lam, mu)` MUST return a frozen `TheoryMetrics` with
`rho = lam / mu`, `L = lam / (mu - lam)`, `Lq = lam ** 2 / (mu * (mu - lam))`,
`W = 1 / (mu - lam)` and `Wq = lam / (mu * (mu - lam))`. Spec: S3.

#### Scenario: Scenario 1 analytic values

- GIVEN `lam = 2.0` and `mu = 3.0`
- WHEN `theoretical_metrics(2.0, 3.0)` is called
- THEN `L == 2.0`, `Lq == 1.333333...`, `W == 1.0`, `Wq == 0.666666...`
- AND `Lq == L - rho` and `Wq == W - 1 / mu` hold within `1e-9`

#### Scenario: Scenario 2 and 3 analytic values

- GIVEN `(lam, mu) = (2.5, 3.0)`
- THEN `L == 5.0`, `Lq == 4.166666...`, `W == 2.0`, `Wq == 1.666666...`
- GIVEN `(lam, mu) = (2.9, 3.0)`
- THEN `L == 29.0`, `Lq == 28.033333...`, `W == 10.0`, `Wq == 9.666666...`

#### Scenario: Unstable input is rejected

- GIVEN `lam = 3.0` and `mu = 3.0`
- WHEN `theoretical_metrics(3.0, 3.0)` is called
- THEN it raises `ValueError` and no metric is returned

### Requirement: Theory metrics SHALL be immutable

`TheoryMetrics` MUST be a frozen dataclass so callers cannot mutate shared
results. Specs: S3, S6.

#### Scenario: Mutation is rejected

- GIVEN a `TheoryMetrics` instance returned by `theoretical_metrics`
- WHEN an attribute assignment is attempted
- THEN a `FrozenInstanceError` is raised
