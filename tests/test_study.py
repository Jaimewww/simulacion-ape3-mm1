"""Shared application service integration tests (tasks 4.6–4.7)."""

from dataclasses import FrozenInstanceError

import pytest

from mm1.controller.study import run_study
from mm1.model import scenarios
from mm1.model.analysis import summarize
from mm1.model.scenarios import Scenario, run_scenarios


def test_study_contains_ordered_model_data() -> None:
    result = run_study(replications=3, sim_time=100.0)
    assert isinstance(result.runs, tuple)
    assert isinstance(result.summaries, tuple)
    assert [run.scenario for run in result.runs] == [1, 1, 1, 2, 2, 2, 3, 3, 3]
    assert [summary.scenario for summary in result.summaries] == [1, 2, 3]
    assert all(summary.replications == 3 for summary in result.summaries)
    assert result.summaries == tuple(summarize(result.runs))


def test_study_replays_seed_and_forwards_parameters() -> None:
    result = run_study(3, 100.0, 123, 10.0)
    assert result == run_study(3, 100.0, 123, 10.0)
    assert result.runs == tuple(run_scenarios(3, 100.0, 123, 10.0))
    assert all(run.warmup == 10.0 and run.sim_time == 100.0 for run in result.runs)


def test_study_result_is_frozen() -> None:
    result = run_study(1, 30.0)
    with pytest.raises(FrozenInstanceError):
        result.runs = ()


def test_study_rejects_unstable_scenario(monkeypatch) -> None:
    monkeypatch.setattr(scenarios, "SCENARIOS", (Scenario(1, 3.0, 3.0, "Probe", "Probe"),))
    with pytest.raises(ValueError, match="El sistema no es estable"):
        run_study(1, 30.0)


def test_study_propagates_invalid_replication_count() -> None:
    with pytest.raises(ValueError, match="replications"):
        run_study(replications=0)
