"""Controller layer — turns a request into model calls and hands the result on.

Owner: Jaime Landazuri (cli) and Richard Chamba (study).
Specs: S4, S6, S14, S16.

This package is the ``C`` of the MVC structure. It is the only layer allowed to
know about more than one layer: it drives ``mm1.model`` and asks ``mm1.view`` to
render. The service in ``study`` is shared by the CLI and the Streamlit page so
the document's numbers and the live resource cannot diverge.

Dependency direction: ``controller`` -> ``model`` (+ ``view`` only to trigger
rendering). ``model`` never imports ``view`` or ``controller``, and ``view``
imports ``model`` but never ``controller``.
"""

from __future__ import annotations

from .cli import main
from .study import StudyResult, run_study

__all__ = [
    "StudyResult",
    "main",
    "run_study",
]
