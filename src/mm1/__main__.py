"""Module entry point for ``python -m mm1``.

Owner: Jaime Landazuri.

This shim only forwards to :func:`mm1.cli.main`; all dispatch logic lives in
``mm1/cli.py`` so the public contract stays unchanged.
"""

from __future__ import annotations

import sys

from mm1.cli import main

if __name__ == "__main__":
    sys.exit(main())
