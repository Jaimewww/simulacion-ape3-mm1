"""Punto de entrada para ejecutar con ``python -m mm1``."""

from __future__ import annotations

import sys

from mm1.controller.cli import main

if __name__ == "__main__":
    sys.exit(main())
