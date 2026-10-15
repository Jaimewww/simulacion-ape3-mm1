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
