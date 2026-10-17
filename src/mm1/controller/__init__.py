"""Capa controlador: conecta modelo y vista.

Orquesta la simulación desde CLI y gestiona los estudios por escenarios.
"""

from __future__ import annotations

from .cli import main
from .study import StudyResult, run_study

__all__ = [
    "StudyResult",
    "main",
    "run_study",
]
