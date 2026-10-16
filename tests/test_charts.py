"""Charts tests for the reporting slice (tasks 5.3-5.5).

Owner: Cael Soto.
Specs: S6 (theory-vs-simulation comparison), S7 (queue and wait charts).

Test-first contract for stage 9 of `CONTRIBUTING.md`: every test here fails
until `src/mm1/view/charts.py` implements its five frozen functions. The
per-run charts use real `run_mm1` runs (stage 3, already merged); the summary
charts use hand-built `ScenarioSummary` fixtures, so these tests never depend
on Richard Chamba's aggregation pipeline. Assertions are file-level only:
existence, size and PNG signature — never pixel comparisons.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib
import pytest

from mm1.model.analysis import ScenarioSummary
from mm1.model.metrics import TheoryMetrics
from mm1.model.simulation import ScenarioRun, run_mm1
from mm1.view.charts import (
    generate_all,
    plot_queue_evolution,
    plot_scenario_comparison,
    plot_theory_vs_sim,
    plot_wait_times,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
THEORY_FIGURE = "teoria_vs_simulacion.png"
COMPARISON_FIGURE = "comparacion_escenarios.png"


def _assert_valid_png(path: Path) -> None:
    """The written image exists, is non-empty and is a real PNG."""
    data = path.read_bytes()
    assert data, f"{path} is empty"
    assert data.startswith(PNG_SIGNATURE), f"{path} is not a PNG file"


def _summary(
    scenario: int,
    lam: float,
    mu: float,
    rho: float,
    L: float,
    Lq: float,
    W: float,
    Wq: float,
    sim_mean_wait: float,
    sim_mean_queue: float,
    sim_mean_in_system: float,
    sim_utilization: float,
    std_wait: float,
    ci95_wait: tuple[float, float],
    rel_error_L: float,
    rel_error_Lq: float,
    rel_error_W: float,
    rel_error_Wq: float,
) -> ScenarioSummary:
    """Build one summary fixture; every value is spelled out at the call site."""
    return ScenarioSummary(
        scenario=scenario,
        lam=lam,
        mu=mu,
        replications=5,
        theory=TheoryMetrics(rho=rho, L=L, Lq=Lq, W=W, Wq=Wq),
        sim_mean_wait=sim_mean_wait,
        sim_mean_queue=sim_mean_queue,
        sim_mean_in_system=sim_mean_in_system,
        sim_utilization=sim_utilization,
        std_wait=std_wait,
        ci95_wait=ci95_wait,
        rel_error_L=rel_error_L,
        rel_error_Lq=rel_error_Lq,
        rel_error_W=rel_error_W,
        rel_error_Wq=rel_error_Wq,
    )


@pytest.fixture
def summaries() -> list[ScenarioSummary]:
    """One fixture per guide scenario, ids 1-3, with hand-computed theory."""
    return [
        _summary(
            1,
            2.0,
            3.0,
            rho=2.0 / 3.0,
            L=2.0,
            Lq=4.0 / 3.0,
            W=1.0,
            Wq=2.0 / 3.0,
            sim_mean_wait=0.70,
            sim_mean_queue=1.40,
            sim_mean_in_system=2.10,
            sim_utilization=0.664,
            std_wait=0.05,
            ci95_wait=(0.66, 0.74),
            rel_error_L=0.05,
            rel_error_Lq=0.05,
            rel_error_W=0.05,
            rel_error_Wq=0.05,
        ),
        _summary(
            2,
            2.5,
            3.0,
            rho=5.0 / 6.0,
            L=5.0,
            Lq=25.0 / 6.0,
            W=2.0,
            Wq=5.0 / 6.0,
            sim_mean_wait=0.85,
            sim_mean_queue=4.30,
            sim_mean_in_system=5.20,
            sim_utilization=0.830,
            std_wait=0.10,
            ci95_wait=(0.78, 0.92),
            rel_error_L=0.04,
            rel_error_Lq=0.032,
            rel_error_W=0.04,
            rel_error_Wq=0.02,
        ),
        _summary(
            3,
            2.9,
            3.0,
            rho=29.0 / 30.0,
            L=29.0,
            Lq=841.0 / 30.0,
            W=10.0,
            Wq=29.0 / 3.0,
            sim_mean_wait=10.50,
            sim_mean_queue=29.80,
            sim_mean_in_system=30.40,
            sim_utilization=0.965,
            std_wait=1.20,
            ci95_wait=(9.10, 11.90),
            rel_error_L=0.0483,
            rel_error_Lq=0.0631,
            rel_error_W=0.054,
            rel_error_Wq=0.0862,
        ),
    ]


@pytest.fixture(scope="module")
def run() -> ScenarioRun:
    """One real engine run (stage 3) reused by the per-run chart tests."""
    return run_mm1(2.0, 3.0, sim_time=200.0, seed=1, scenario=1)


@pytest.fixture(scope="module")
def runs() -> list[ScenarioRun]:
    """One real run per guide scenario, ids 1-3, as the study service yields them."""
    rates = ((2.0, 3.0), (2.5, 3.0), (2.9, 3.0))
    return [
        run_mm1(lam, mu, sim_time=100.0, seed=scenario, scenario=scenario)
        for scenario, (lam, mu) in enumerate(rates, start=1)
    ]


def test_charts_module_forces_the_agg_backend() -> None:
    """Importing the module is enough to render headless (decision D6)."""
    assert matplotlib.get_backend().lower() == "agg"


def test_plot_queue_evolution_writes_a_valid_png(run: ScenarioRun, tmp_path: Path) -> None:
    """The queue chart exists, is non-empty and is a PNG (str path accepted)."""
    written = plot_queue_evolution(run, str(tmp_path / "cola.png"))
    assert isinstance(written, Path)
    assert written.exists()
    _assert_valid_png(written)


def test_plot_wait_times_writes_a_valid_png(run: ScenarioRun, tmp_path: Path) -> None:
    """The wait chart exists, is non-empty and is a PNG."""
    written = plot_wait_times(run, tmp_path / "espera.png")
    assert isinstance(written, Path)
    assert written.exists()
    _assert_valid_png(written)


def test_plot_functions_survive_an_empty_run(tmp_path: Path) -> None:
    """A horizon shorter than the first arrival still renders both charts."""
    empty = run_mm1(0.01, 3.0, sim_time=1.0, seed=1)
    assert empty.n_customers == 0

    queue_path = plot_queue_evolution(empty, tmp_path / "cola_vacia.png")
    wait_path = plot_wait_times(empty, tmp_path / "espera_vacia.png")
    _assert_valid_png(queue_path)
    _assert_valid_png(wait_path)


def test_plot_theory_vs_sim_writes_a_valid_png(
    summaries: Sequence[ScenarioSummary], tmp_path: Path
) -> None:
    """The theory-versus-simulation chart is a non-empty PNG."""
    written = plot_theory_vs_sim(summaries, tmp_path / THEORY_FIGURE)
    assert isinstance(written, Path)
    _assert_valid_png(written)


def test_plot_scenario_comparison_writes_a_valid_png(
    summaries: Sequence[ScenarioSummary], tmp_path: Path
) -> None:
    """The scenario comparison chart is a non-empty PNG."""
    written = plot_scenario_comparison(summaries, tmp_path / COMPARISON_FIGURE)
    assert isinstance(written, Path)
    _assert_valid_png(written)


def test_generate_all_writes_every_figure_inside_out_dir(
    runs: Sequence[ScenarioRun],
    summaries: Sequence[ScenarioSummary],
    tmp_path: Path,
) -> None:
    """Every run gets its two charts plus the two summary figures, once each."""
    paths = generate_all(runs, summaries, tmp_path)

    assert len(paths) == 2 * len(runs) + 2
    assert len({path.name for path in paths}) == len(paths), "duplicated figure names"

    for path in paths:
        assert path.parent == tmp_path, f"{path} is outside the output directory"
        _assert_valid_png(path)

    names = [path.name for path in paths]
    assert names.count(THEORY_FIGURE) == 1
    assert names.count(COMPARISON_FIGURE) == 1


def test_generate_all_overwrites_without_duplicates(
    runs: Sequence[ScenarioRun],
    summaries: Sequence[ScenarioSummary],
    tmp_path: Path,
) -> None:
    """A second identical call rewrites the same files, leaving no duplicates."""
    first = generate_all(runs, summaries, tmp_path)
    assert len(first) > 2

    second = generate_all(runs, summaries, tmp_path)

    assert [path.name for path in second] == [path.name for path in first]
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(path.name for path in first)
    for path in second:
        _assert_valid_png(path)
