"""Animation tests for the reporting slice (tasks 6.1-6.2).

Owner: Domenica Rojas.
Specs: S7 (queue behaviour), S19 (no interactive interface, headless animation),
S20 (this re-planification onto the command line).

Test-first contract for stage 10 of `CONTRIBUTING.md`: every test here fails until
`src/mm1/view/animation.py` implements its three frozen functions.

Two deliberate properties keep this suite independent from the encoder:

* The pure helpers (``frame_frames`` and ``queue_animation_figure``) are exercised
  without ever running the encoder, so no display and no video backend is needed.
* The test that actually writes ``cola.mp4`` and ``cola.gif`` is skipped when
  ``ffmpeg`` is not installed, because the MP4 writer is the only part of the module
  that needs the external binary; the GIF writer only needs Pillow.

The per-run fixtures use real ``run_mm1`` runs (stage 3, already merged) with a short
horizon, so the suite stays fast.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib
import pytest

# The module under test forces Agg before importing pyplot; the test does the same
# so the figure assertions never need a display.
matplotlib.use("Agg")
from matplotlib import animation
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from mm1.model.simulation import ScenarioRun, run_mm1
from mm1.view.animation import frame_frames, queue_animation_figure, render_queue_animation

MP4_NAME = "cola.mp4"
GIF_NAME = "cola.gif"

# PNG and container signatures, so a file is proven to be a real image/video and
# never compared pixel by pixel.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
GIF_SIGNATURE = b"GIF8"
MP4_FTYP_OFFSET = 4

FFMPEG_AVAILABLE = "ffmpeg" in animation.writers.list()
needs_ffmpeg = pytest.mark.skipif(
    not FFMPEG_AVAILABLE,
    reason="ffmpeg is not installed: the GIF path still runs, the MP4 encoder is skipped",
)


def _trace(entries: int, step: float = 1.0) -> list[tuple[float, int]]:
    """Build a synthetic piecewise-constant trace of ``entries`` entries."""
    return [(index * step, index % 3) for index in range(entries)]


def _run() -> ScenarioRun:
    """Return a real, short, stable-scenario run produced by the engine."""
    return run_mm1(2.0, 3.0, sim_time=200.0, seed=42, scenario=1)


def _is_prefix(frame: Sequence[tuple[float, int]], trace: Sequence[tuple[float, int]]) -> bool:
    """True when every point of ``frame`` that belongs to the trace is a prefix."""
    return list(frame[: len(trace)]) == list(trace[: len(frame)])


# SPEC: S19, S20 — the Agg backend is forced so nothing needs a display.
def test_backend_is_headless() -> None:
    """Rendering never requires a display."""
    assert matplotlib.get_backend().lower() == "agg"


# SPEC: S7, S20 — at most max_frames sub-traces, all starting at the first entry,
# the last one covering the whole trace.
def test_frame_frames_is_bounded_and_covers_the_trace() -> None:
    """A 500-entry trace sampled with max_frames=50 is bounded and complete."""
    trace = _trace(500)
    frames = frame_frames(trace, 500.0, 50)

    assert len(frames) <= 50
    assert frames[0] == [trace[0]], "every frame must start at the first trace entry"
    assert all(frame[:1] == [trace[0]] for frame in frames)
    assert all(_is_prefix(frame, trace) for frame in frames)
    assert [len(frame) for frame in frames] == sorted(len(frame) for frame in frames)
    assert len({len(frame) for frame in frames}) == len(frames), "frames must grow"
    assert frames[-1][: len(trace)] == trace, "the last frame must cover the whole trace"


# SPEC: S20 — a short trace is returned whole.
def test_frame_frames_returns_a_short_trace_whole() -> None:
    """Five entries with room for 50 frames keep one frame per entry."""
    trace = _trace(5)
    frames = frame_frames(trace, 5.0, 50)

    assert len(frames) <= 50
    assert [len(frame[: len(trace)]) for frame in frames] == [1, 2, 3, 4, 5]
    assert frames[-1][: len(trace)] == trace


# SPEC: S20 — max_frames must be positive.
def test_frame_frames_rejects_a_non_positive_max_frames() -> None:
    """Zero and negative bounds fail instead of returning a bogus animation."""
    trace = _trace(10)
    with pytest.raises(ValueError):
        frame_frames(trace, 10.0, 0)
    with pytest.raises(ValueError):
        frame_frames(trace, 10.0, -3)


# SPEC: S2, S20 — the step function is closed at the simulated horizon, so the
# animation spans the whole simulated window (same convention as the static chart).
def test_frame_frames_closes_the_last_frame_at_the_horizon() -> None:
    """The last frame reaches sim_time, the intermediate ones do not."""
    trace = _trace(10)
    frames = frame_frames(trace, 12.5, 4)

    assert frames[-1][-1] == (12.5, trace[-1][1])
    assert frames[-1][: len(trace)] == trace
    assert all(frame[-1][0] < 12.5 for frame in frames[:-1])


# SPEC: S1, S2 — the pure figure helper returns a Figure and an update callable,
# with Spanish labels for the report, and runs no encoder.
def test_queue_animation_figure_returns_a_figure_and_an_update_callable() -> None:
    """The helper builds the artists and exposes the per-frame update function."""
    fig, update = queue_animation_figure(_run(), 6)
    try:
        assert isinstance(fig, Figure)
        assert callable(update)

        artists = update(0)
        assert isinstance(artists, tuple)

        axes = fig.axes[0]
        assert axes.get_xlabel() == "Tiempo simulado"
        assert axes.get_ylabel() == "Clientes en la cola"
        assert "cola" in axes.get_title().lower()
        assert axes.get_legend() is not None, "S2 requires a Spanish legend"
    finally:
        plt.close(fig)


# SPEC: S4 — building the figure writes nothing: the encoder is the renderer's job.
def test_queue_animation_figure_runs_no_encoder(tmp_path, monkeypatch) -> None:
    """No file is written anywhere while the figure is being built."""
    monkeypatch.chdir(tmp_path)
    fig, _ = queue_animation_figure(_run(), 4)
    plt.close(fig)

    assert list(tmp_path.iterdir()) == []


# SPEC: S2 — no dates or timestamps: the same input renders the same animation.
def test_figure_rendering_is_deterministic(tmp_path) -> None:
    """Two independently built figures render frame 0 to identical PNG bytes."""
    run = _run()
    first, second = tmp_path / "first.png", tmp_path / "second.png"

    for path in (first, second):
        fig, update = queue_animation_figure(run, 5)
        update(0)
        fig.savefig(path, dpi=100)
        plt.close(fig)

    assert first.read_bytes().startswith(PNG_SIGNATURE)
    assert first.read_bytes() == second.read_bytes()


# SPEC: S2, S19 — both files are written, non-empty, and the figure is closed.
@needs_ffmpeg
def test_render_queue_animation_writes_both_files(tmp_path) -> None:
    """The renderer writes a real MP4 and a real GIF and leaves no open figure."""
    paths = render_queue_animation(_run(), tmp_path, fps=5, max_frames=6)

    assert [Path(path).name for path in paths] == [MP4_NAME, GIF_NAME]
    assert all(Path(path) == tmp_path / Path(path).name for path in paths)

    mp4, gif = (Path(path) for path in paths)
    assert mp4.exists() and mp4.stat().st_size > 0
    assert gif.exists() and gif.stat().st_size > 0
    assert mp4.read_bytes()[MP4_FTYP_OFFSET : MP4_FTYP_OFFSET + 4] == b"ftyp"
    assert gif.read_bytes().startswith(GIF_SIGNATURE)
    assert plt.get_fignums() == [], "the renderer must close its figure"


# SPEC: S1 — the frozen signature accepts a directory given as str or as Path.
@needs_ffmpeg
def test_render_queue_animation_accepts_a_string_directory(tmp_path) -> None:
    """A str output directory is honored as well as a Path."""
    paths = render_queue_animation(_run(), str(tmp_path), fps=5, max_frames=4)

    assert all(Path(path).exists() for path in paths)
    assert (tmp_path / MP4_NAME).exists()
    assert (tmp_path / GIF_NAME).exists()


# SPEC: S2, S20 — same input, same GIF: the encoder adds no timestamp either.
@needs_ffmpeg
def test_render_queue_animation_gif_is_deterministic(tmp_path) -> None:
    """Two renders of the same run produce byte-identical GIF files."""
    run = _run()
    first_dir, second_dir = tmp_path / "a", tmp_path / "b"

    render_queue_animation(run, first_dir, fps=5, max_frames=4)
    render_queue_animation(run, second_dir, fps=5, max_frames=4)

    assert (first_dir / GIF_NAME).read_bytes() == (second_dir / GIF_NAME).read_bytes()
