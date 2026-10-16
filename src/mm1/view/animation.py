"""Headless queue animation for the M/M/1 practice.

Owner: Domenica Rojas.
Specs: S7 (queue behaviour), S19 (no interactive interface), S20 (stage-10
re-planification onto the command line).

The practice has no interactive interface (the teacher required it), so the visual
resource is this module: it renders the queue evolution of one ``ScenarioRun`` to an
MP4 and a GIF file that the command line writes when ``--animate`` is given. It is a
view, so it renders only: the run arrives already executed by the engine and no
domain result is computed here.

Rendering rules frozen by the plan (decisions D16 and D17):

* The non-interactive ``Agg`` backend is forced at module level, **before** pyplot
  is imported, so nothing ever needs a display.
* Both ``cola.mp4`` (FFmpeg writer) and ``cola.gif`` (Pillow writer) are written, and
  the figure is closed afterwards so repeated calls never accumulate figures.
* Axis labels, title and legend are in Spanish because the animation goes into the
  report; identifiers and comments stay in English.
* No dates or wall-clock timestamps are rendered, so the same input always produces
  the same animation.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

import matplotlib

# Decisions D16 and D17: headless backend, set before pyplot is imported. The call
# deliberately sits between the two imports.
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.figure import Figure

from ..model.simulation import ScenarioRun

# File names written by render_queue_animation (Spanish: they are report artifacts,
# like the CLI's own comparacion.csv).
MP4_NAME = "cola.mp4"
GIF_NAME = "cola.gif"

# Figure geometry; 800x450 keeps the H.264 encoder on even dimensions.
FIGURE_SIZE = (8.0, 4.5)


# SPEC: S20 — the queue trace is sampled into growing prefixes, the last one
# covering the whole trace plus the simulated horizon.
def frame_frames(
    trace: Sequence[tuple[float, int]], sim_time: float, max_frames: int
) -> list[list[tuple[float, int]]]:
    """Sample ``trace`` into at most ``max_frames`` growing sub-traces.

    The first sub-trace holds only the first trace entry, every sub-trace is a prefix
    of the trace, and the last one covers the whole trace. Because the queue length
    is a piecewise-constant function, the last sub-trace is closed at ``sim_time``
    with the final queue length, exactly like the static queue chart, so the
    animation spans the whole simulated window.

    Args:
        trace: ``(time, queue_length)`` pairs sorted by time.
        sim_time: Simulated horizon used to close the last sub-trace.
        max_frames: Upper bound on the number of sub-traces; must be positive.

    Returns:
        The sampled sub-traces, at most ``max_frames`` of them.

    Raises:
        ValueError: If ``max_frames`` is not positive, or if ``trace`` is empty.
    """
    if max_frames <= 0:
        raise ValueError("max_frames debe ser mayor que 0")
    entries = list(trace)
    if not entries:
        raise ValueError("la traza no puede estar vacia")

    total = len(entries)
    count = min(max_frames, total)
    if count == 1:
        boundaries = [total]
    else:
        span = (total - 1) / (count - 1)
        boundaries = [1 + round(span * index) for index in range(count)]

    frames = [entries[:boundary] for boundary in boundaries]
    frames[-1].append((float(sim_time), entries[-1][1]))
    return frames


# SPEC: S1, S2, S19 — pure helper: it builds the artists and returns the per-frame
# update callable, and never runs the encoder.
def queue_animation_figure(run: ScenarioRun, frames: int) -> tuple[Figure, Callable[[int], tuple]]:
    """Build the animated queue figure of ``run`` and its update callable.

    The axes are fixed to the full sampled trace, so the visible limits never jump
    while the line grows frame by frame.

    Args:
        run: Simulation run whose ``queue_trace`` is animated.
        frames: Upper bound on the number of animation frames.

    Returns:
        The figure and the ``update(frame_index) -> tuple`` callable that redraws the
        line and the simulated-time caption for one frame.
    """
    sampled = frame_frames(run.queue_trace, run.sim_time, frames)
    full = sampled[-1]
    times = [time for time, _ in full]
    lengths = [length for _, length in full]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    (line,) = ax.step(times, lengths, where="post", label="Clientes en la cola")
    ax.axhline(
        run.mean_queue,
        linestyle="--",
        label=f"Promedio simulado ({run.mean_queue:.2f})",
    )
    caption = ax.text(0.02, 0.93, "", transform=ax.transAxes)

    ax.set_xlim(0.0, max(float(run.sim_time), 1.0))
    ax.set_ylim(0.0, max(lengths) + 1)
    ax.set_xlabel("Tiempo simulado")
    ax.set_ylabel("Clientes en la cola")
    ax.set_title(f"Evolución de la cola — Escenario {run.scenario} (λ={run.lam:g}, μ={run.mu:g})")
    ax.legend(loc="upper left")
    ax.grid(linestyle=":", alpha=0.4)

    def update(index: int) -> tuple:
        """Redraw the line and the caption for frame ``index``."""
        snapshot = sampled[index]
        line.set_data([time for time, _ in snapshot], [length for _, length in snapshot])
        caption.set_text(f"t = {snapshot[-1][0]:.1f}  ·  cola = {snapshot[-1][1]}")
        return (line, caption)

    return fig, update


# SPEC: S1, S2, S19 — render one run to cola.mp4 and cola.gif, headless.
def render_queue_animation(
    run: ScenarioRun, out_dir: str | Path, fps: int = 20, max_frames: int = 200
) -> list[Path]:
    """Render the queue animation of ``run`` into ``out_dir``.

    Both ``cola.mp4`` (FFmpeg writer) and ``cola.gif`` (Pillow writer) are written,
    and the figure is always closed, including when an encoder fails.

    Args:
        run: Completed simulation run produced by the engine.
        out_dir: Directory that receives the two files; it is created when missing.
        fps: Frames per second of both animations.
        max_frames: Upper bound on the number of frames, passed to the sampler.

    Returns:
        The paths of ``cola.mp4`` and ``cola.gif``, in that order.

    Raises:
        ValueError: If ``fps`` is not positive, or if ``max_frames`` is not positive.
    """
    if fps <= 0:
        raise ValueError("fps debe ser mayor que 0")

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    fig, update = queue_animation_figure(run, max_frames)
    frame_count = len(frame_frames(run.queue_trace, run.sim_time, max_frames))
    anim = FuncAnimation(fig, update, frames=frame_count, blit=True)

    mp4_path = out / MP4_NAME
    gif_path = out / GIF_NAME
    try:
        anim.save(mp4_path, writer=FFMpegWriter(fps=fps))
        anim.save(gif_path, writer=PillowWriter(fps=fps))
    finally:
        plt.close(fig)

    return [mp4_path, gif_path]


__all__ = ["frame_frames", "queue_animation_figure", "render_queue_animation"]
