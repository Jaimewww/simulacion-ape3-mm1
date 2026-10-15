"""Thin Streamlit entry point — composition root of the interactive flow.

Owner: Domenica Rojas.
Specs: S11 (interactive graphic resource), S15 (Streamlit), S16 (view layer).

Kept deliberately thin so the documented command stays short:

    streamlit run app/streamlit_app.py

All rendering lives in ``mm1.view.streamlit_view``. Requires the package to be
installed (``pip install -e .``) or ``src/`` on ``PYTHONPATH``; if neither is
done the script stops with the exact command to run instead of a bare traceback.
"""

from __future__ import annotations

try:
    from mm1.view.streamlit_view import render
except ModuleNotFoundError as exc:  # pragma: no cover - actionable message
    raise SystemExit(
        "No se encontró el paquete 'mm1'. Ejecutá:\n"
        "    pip install -e .\n"
        "o bien:\n"
        "    PYTHONPATH=src streamlit run app/streamlit_app.py"
    ) from exc

if __name__ == "__main__":
    render()
