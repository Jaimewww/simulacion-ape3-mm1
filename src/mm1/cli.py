"""Command-line entry point for the M/M/1 practice.

Owner: Jaime Landazuri.
Specs: S4 (pseudocode workflow), S14 (agent-executable entry point).

This module exposes ``main`` so the whole workflow (simulate, compare, chart,
export) can be driven from a single command. The concrete flags are defined by
the openspec plan; until then the body is a stub.
"""

from __future__ import annotations

from collections.abc import Sequence


# SPEC: S4, S14 — run the end-to-end workflow from the command line.
def main(argv: Sequence[str] | None = None) -> int:
    """Run the M/M/1 workflow and return a process exit code.

    Args:
        argv: Command-line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        The process exit code (``0`` on success).
    """
    raise NotImplementedError("Jaime Landazuri — see openspec plan")
