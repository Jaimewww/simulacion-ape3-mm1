"""Comparison table tests for the reporting slice (tasks 5.1 and 5.2).

Owner: Cael Soto.
Specs: S6 (compare theory and simulation with a table), S7 (deliverable).

Test-first contract for stage 8 of `CONTRIBUTING.md`: every test here fails
until `src/mm1/view/tables.py` implements its three frozen functions. The
fixtures are hand-built `ScenarioSummary` values with the guide's published
theory (L=2.0, Lq=4/3, W=1.0, Wq=2/3 for lambda=2.0, mu=3.0), so the tests
never depend on Richard Chamba's aggregation pipeline.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas
import pytest
from pandas.api.types import is_numeric_dtype

from mm1.model.analysis import ScenarioSummary
from mm1.model.metrics import TheoryMetrics
from mm1.view.tables import comparison_dataframe, to_latex, write_csv

# The frozen 19-column schema of the reporting spec, in order.
COLUMNS = (
    "scenario",
    "lam",
    "mu",
    "rho",
    "L",
    "Lq",
    "W",
    "Wq",
    "sim_mean_wait",
    "sim_mean_queue",
    "sim_mean_in_system",
    "sim_utilization",
    "std_wait",
    "ci95_low",
    "ci95_high",
    "rel_error_L",
    "rel_error_Lq",
    "rel_error_W",
    "rel_error_Wq",
)


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


@pytest.fixture
def frame(summaries: Sequence[ScenarioSummary]) -> pandas.DataFrame:
    return comparison_dataframe(summaries)


def test_frame_exposes_exactly_the_19_frozen_columns(frame: pandas.DataFrame) -> None:
    """The schema is the frozen one, in the frozen order, nothing extra."""
    assert list(frame.columns) == list(COLUMNS)


def test_one_row_per_scenario_sorted_by_id(summaries: Sequence[ScenarioSummary]) -> None:
    """Row order follows the scenario id even when the input does not."""
    shuffled = list(reversed(summaries))
    assert comparison_dataframe(shuffled)["scenario"].tolist() == [1, 2, 3]
    assert len(comparison_dataframe(shuffled)) == 3


def test_theory_columns_come_from_the_theoretical_model(
    frame: pandas.DataFrame, summaries: Sequence[ScenarioSummary]
) -> None:
    """rho, L, Lq, W and Wq echo summary.theory, not simulated values."""
    for summary in summaries:
        row = frame[frame["scenario"] == summary.scenario].iloc[0]
        assert (row["rho"], row["L"], row["Lq"], row["W"], row["Wq"]) == (
            summary.theory.rho,
            summary.theory.L,
            summary.theory.Lq,
            summary.theory.W,
            summary.theory.Wq,
        )


def test_simulated_and_error_columns_echo_the_summary(
    frame: pandas.DataFrame, summaries: Sequence[ScenarioSummary]
) -> None:
    """sim_* and std_wait are the homonymous fields; the CI splits into two columns."""
    echoed = (
        "sim_mean_wait",
        "sim_mean_queue",
        "sim_mean_in_system",
        "sim_utilization",
        "std_wait",
        "rel_error_L",
        "rel_error_Lq",
        "rel_error_W",
        "rel_error_Wq",
    )
    for summary in summaries:
        row = frame[frame["scenario"] == summary.scenario].iloc[0]
        for column in echoed:
            assert row[column] == getattr(summary, column), column
        assert (row["ci95_low"], row["ci95_high"]) == summary.ci95_wait


def test_every_column_is_numeric(frame: pandas.DataFrame) -> None:
    """All 19 columns carry numbers, so the CSV/LaTeX export never leaks text."""
    for column in COLUMNS:
        assert is_numeric_dtype(frame[column]), f"{column} is not numeric"


def test_ci95_bounds_are_ordered(frame: pandas.DataFrame) -> None:
    """The Student-t interval of the mean keeps lower <= upper."""
    assert (frame["ci95_low"] <= frame["ci95_high"]).all()


def test_write_csv_returns_an_existing_non_empty_path(
    frame: pandas.DataFrame, tmp_path: Path
) -> None:
    """write_csv accepts a str path and returns the written Path."""
    csv_path = write_csv(frame, str(tmp_path / "comparacion.csv"))
    assert isinstance(csv_path, Path)
    assert csv_path.exists()
    assert csv_path.stat().st_size > 0


def test_csv_round_trips_schema_rows_and_values(frame: pandas.DataFrame, tmp_path: Path) -> None:
    """The CSV re-reads with the same 19 columns, 3 rows and values."""
    csv_path = write_csv(frame, tmp_path / "comparacion.csv")
    reread = pandas.read_csv(csv_path)
    assert list(reread.columns) == list(COLUMNS)
    assert len(reread) == 3
    pandas.testing.assert_frame_equal(reread, frame, check_exact=False, rtol=1e-12)


def test_to_latex_writes_a_referencable_table(frame: pandas.DataFrame, tmp_path: Path) -> None:
    """The LaTeX export is a table float with a caption and a label."""
    tex_path = to_latex(frame, tmp_path / "comparacion.tex")
    assert isinstance(tex_path, Path)
    assert tex_path.exists()
    assert tex_path.stat().st_size > 0

    text = tex_path.read_text(encoding="utf-8")
    assert "\\begin{table}" in text
    assert "\\begin{tabular}" in text
    assert "\\caption{" in text
    assert "\\label{tab:" in text
    assert "\\end{table}" in text


def test_repeated_writes_overwrite_the_same_files(frame: pandas.DataFrame, tmp_path: Path) -> None:
    """A second export overwrites in place instead of leaving duplicates."""
    write_csv(frame, tmp_path / "comparacion.csv")
    write_csv(frame, tmp_path / "comparacion.csv")
    to_latex(frame, tmp_path / "comparacion.tex")
    to_latex(frame, tmp_path / "comparacion.tex")

    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "comparacion.csv",
        "comparacion.tex",
    ]
