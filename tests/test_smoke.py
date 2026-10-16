"""Structural smoke tests for the ``mm1`` scaffold (APE 003).

This is the scaffold's only test. It checks that the package imports cleanly and
that the frozen public interface exists with the expected arity. It asserts
structure, not behaviour. Every team member adds their own behaviour tests (RED
first) in their own file.
"""

from __future__ import annotations

import dataclasses
import importlib
import inspect

import pytest

import mm1

SUBMODULES = (
    "mm1.model.metrics",
    "mm1.model.simulation",
    "mm1.model.scenarios",
    "mm1.model.analysis",
    "mm1.view.tables",
    "mm1.view.charts",
    "mm1.controller.cli",
)

EXPECTED_PARAMETERS = {
    "mm1.model.metrics": {
        "utilization": ("lam", "mu"),
        "is_stable": ("lam", "mu"),
        "theoretical_metrics": ("lam", "mu"),
    },
    "mm1.model.simulation": {
        "run_mm1": ("lam", "mu", "sim_time", "seed", "scenario", "warmup"),
    },
    "mm1.model.scenarios": {
        "run_scenarios": ("replications", "sim_time", "base_seed", "warmup"),
    },
    "mm1.model.analysis": {
        "confidence_interval": ("values", "confidence"),
        "relative_error": ("simulated", "theoretical"),
        "summarize": ("runs",),
    },
    "mm1.view.tables": {
        "comparison_dataframe": ("summaries",),
        "write_csv": ("df", "path"),
        "to_latex": ("df", "path"),
    },
    "mm1.view.charts": {
        "plot_queue_evolution": ("run", "path"),
        "plot_wait_times": ("run", "path"),
        "plot_theory_vs_sim": ("summaries", "path"),
        "plot_scenario_comparison": ("summaries", "path"),
        "generate_all": ("runs", "summaries", "out_dir"),
    },
    "mm1.controller.cli": {
        "main": ("argv",),
    },
}

EXPECTED_DATACLASS_FIELDS = {
    "mm1.model.metrics": {
        "TheoryMetrics": ("rho", "L", "Lq", "W", "Wq"),
    },
    "mm1.model.simulation": {
        "CustomerRecord": (
            "customer_id",
            "arrival_time",
            "service_start",
            "departure_time",
            "wait_time",
            "service_time",
        ),
        "ScenarioRun": (
            "scenario",
            "lam",
            "mu",
            "seed",
            "sim_time",
            "warmup",
            "n_customers",
            "mean_wait",
            "mean_queue",
            "mean_system_time",
            "mean_in_system",
            "utilization",
            "customers",
            "queue_trace",
        ),
    },
    "mm1.model.scenarios": {
        "Scenario": ("id", "lam", "mu", "label", "condition"),
    },
    "mm1.model.analysis": {
        "ScenarioSummary": (
            "scenario",
            "lam",
            "mu",
            "replications",
            "theory",
            "sim_mean_wait",
            "sim_mean_queue",
            "sim_mean_in_system",
            "sim_utilization",
            "std_wait",
            "ci95_wait",
            "rel_error_L",
            "rel_error_Lq",
            "rel_error_W",
            "rel_error_Wq",
        ),
    },
}


def test_package_import_and_all() -> None:
    """``mm1`` imports cleanly and every ``__all__`` name is bound."""
    assert mm1.__all__
    for name in mm1.__all__:
        assert hasattr(mm1, name), f"mm1.{name} is missing"


@pytest.mark.parametrize("module_name", SUBMODULES)
def test_submodule_imports(module_name: str) -> None:
    """Each frozen submodule can be imported."""
    assert importlib.import_module(module_name) is not None


@pytest.mark.parametrize(
    ("module_name", "func_name"),
    [(module, func) for module, funcs in EXPECTED_PARAMETERS.items() for func in funcs],
)
def test_function_signatures(module_name: str, func_name: str) -> None:
    """Frozen functions exist with exactly the expected parameter names."""
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    assert inspect.isfunction(func), f"{module_name}.{func_name} is not a function"
    parameters = tuple(inspect.signature(func).parameters)
    assert parameters == EXPECTED_PARAMETERS[module_name][func_name]


@pytest.mark.parametrize(
    ("module_name", "class_name"),
    [(module, cls) for module, classes in EXPECTED_DATACLASS_FIELDS.items() for cls in classes],
)
def test_dataclass_fields(module_name: str, class_name: str) -> None:
    """Frozen dataclasses exist with exactly the expected fields."""
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    assert dataclasses.is_dataclass(cls), f"{module_name}.{class_name} is not a dataclass"
    fields = tuple(field.name for field in dataclasses.fields(cls))
    assert fields == EXPECTED_DATACLASS_FIELDS[module_name][class_name]


def test_scenarios_catalogue_is_a_tuple() -> None:
    """``SCENARIOS`` exists and is a tuple (its contents belong to Richard Chamba)."""
    assert isinstance(importlib.import_module("mm1.model.scenarios").SCENARIOS, tuple)


# --------------------------------------------------------------------------- #
# CLI behaviour (stage 4, tasks.md 3.3)
# --------------------------------------------------------------------------- #

SINGLE_RUN_ARGS = ["--lam", "2.0", "--mu", "3.0", "--sim-time", "200", "--seed", "42"]
FROZEN_FLAGS = (
    "--lam",
    "--mu",
    "--scenarios",
    "--replications",
    "--sim-time",
    "--seed",
    "--warmup",
    "--out",
)


@pytest.fixture()
def cli():
    """The CLI module under test."""
    return importlib.import_module("mm1.controller.cli")


def test_cli_single_run_succeeds(cli, capsys) -> None:
    """A stable single-scenario probe exits 0 and compares theory with simulation."""
    code = cli.main([*SINGLE_RUN_ARGS])
    output = capsys.readouterr().out

    assert code == 0
    assert "teórica" in output and "simulada" in output
    assert "Wq" in output and "utilización" in output and "semilla" in output


def test_cli_refuses_unstable_input(cli, tmp_path, capsys) -> None:
    """``lam >= mu`` prints the guide message, returns non-zero and writes nothing."""
    code = cli.main(["--lam", "3.0", "--mu", "3.0", "--out", str(tmp_path)])
    output = capsys.readouterr().out

    assert code != 0
    assert "El sistema no es estable" in output
    assert list(tmp_path.iterdir()) == []


def test_cli_reports_invalid_rates(cli, capsys) -> None:
    """A zero rate is reported as a message instead of a traceback."""
    code = cli.main(["--lam", "0", "--mu", "3.0"])

    assert code != 0
    assert "positivas" in capsys.readouterr().out


def test_cli_requires_both_rates(cli) -> None:
    """Passing only one of ``--lam``/``--mu`` is a usage error."""
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--lam", "2.0"])

    assert exit_info.value.code == 2


def test_cli_rejects_mixing_modes(cli) -> None:
    """``--scenarios`` cannot be combined with the single-run flags."""
    with pytest.raises(SystemExit):
        cli.main(["--scenarios", "--lam", "2.0", "--mu", "3.0"])


def test_cli_exposes_every_frozen_flag(cli, capsys) -> None:
    """``--help`` exits 0 and documents the whole frozen flag surface."""
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--help"])

    assert exit_info.value.code == 0
    help_text = capsys.readouterr().out
    for flag in FROZEN_FLAGS:
        assert flag in help_text


def test_cli_scenarios_mode_uses_the_shared_service(cli, monkeypatch, tmp_path) -> None:
    """Scenarios mode goes through ``controller.study.run_study`` with parsed options."""
    seen: dict[str, object] = {}

    def fake_run_study(**kwargs: object):
        seen.update(kwargs)
        raise RuntimeError("run_study reached")

    monkeypatch.setattr(cli, "run_study", fake_run_study)
    with pytest.raises(RuntimeError, match="run_study reached"):
        cli.main(
            [
                "--scenarios",
                "--replications",
                "3",
                "--sim-time",
                "100",
                "--out",
                str(tmp_path),
            ]
        )

    assert seen == {
        "replications": 3,
        "sim_time": 100.0,
        "base_seed": 42,
        "warmup": 0.0,
    }


def test_cli_scenarios_mode_writes_every_reported_artifact(cli, tmp_path) -> None:
    """One command regenerates the report's table (CSV and LaTeX) and figures.

    This is the integration promise of tasks.md 7.2: the document's table and
    figures MUST come out of a single command, so the LaTeX export cannot be
    left to a manual step.
    """
    code = cli.main(
        [
            "--scenarios",
            "--replications",
            "1",
            "--sim-time",
            "50",
            "--out",
            str(tmp_path),
        ]
    )

    assert code == 0
    assert (tmp_path / "comparacion.csv").stat().st_size > 0
    assert (tmp_path / "comparacion.tex").stat().st_size > 0
    assert (tmp_path / "teoria_vs_simulacion.png").stat().st_size > 0
    assert (tmp_path / "comparacion_escenarios.png").stat().st_size > 0
