"""Guide catalogue and reproducible replication tests (tasks 4.1–4.2)."""

from dataclasses import FrozenInstanceError, astuple

import pytest

from mm1.model import scenarios
from mm1.model.scenarios import SCENARIOS, Scenario, run_scenarios


def test_catalogue_matches_guide() -> None:
    assert tuple(map(astuple, SCENARIOS)) == (
        (1, 2.0, 3.0, "Escenario 1", "Sistema estable"),
        (2, 2.5, 3.0, "Escenario 2", "Mayor utilización"),
        (3, 2.9, 3.0, "Escenario 3", "Cerca de saturación"),
    )
    with pytest.raises(FrozenInstanceError):
        SCENARIOS[0].lam = 9.0


def test_replication_order_and_parameters() -> None:
    runs = run_scenarios(replications=3, sim_time=100.0, base_seed=42, warmup=10.0)
    assert [run.scenario for run in runs] == [1, 1, 1, 2, 2, 2, 3, 3, 3]
    assert [(run.lam, run.mu) for run in runs] == [
        (s.lam, s.mu) for s in SCENARIOS for _ in range(3)
    ]
    assert all(run.sim_time == 100.0 and run.warmup == 10.0 for run in runs)
    assert len({run.seed for run in runs}) == 9


def test_seeds_and_results_are_reproducible() -> None:
    first = run_scenarios(3, 100.0, 42)
    assert first == run_scenarios(3, 100.0, 42)
    assert [r.seed for r in first] != [r.seed for r in run_scenarios(3, 100.0, 43)]


def test_seeds_do_not_depend_on_catalogue_order_or_replication_count(monkeypatch) -> None:
    first = run_scenarios(2, 30.0)
    monkeypatch.setattr(scenarios, "SCENARIOS", tuple(reversed(SCENARIOS)))
    extended = run_scenarios(3, 30.0)
    for run in first:
        peers = [r for r in extended if r.scenario == run.scenario]
        assert run in peers[:2]


@pytest.mark.parametrize("replications", [0, -1, 1.5, True])
def test_invalid_replication_counts_are_rejected(replications) -> None:
    with pytest.raises(ValueError, match="replications"):
        run_scenarios(replications=replications)


def test_unstable_scenario_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(scenarios, "SCENARIOS", (Scenario(1, 3.0, 3.0, "Probe", "Probe"),))
    with pytest.raises(ValueError, match="El sistema no es estable"):
        run_scenarios(1, 30.0)
