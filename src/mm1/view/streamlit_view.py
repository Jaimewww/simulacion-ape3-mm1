"""Interactive Streamlit page of the M/M/1 practice.

Owner: Domenica Rojas.
Specs: S7 (charts), S11 (interactive graphic resource), S15 (Streamlit), S16 (view
layer), S18 (the visual resource is the final deliverable).

This is the ``V`` of the interactive flow. It renders and it collects input; it
does NOT compute domain results — it asks ``mm1.controller.run_study`` for them
and renders whatever comes back, so the live resource shows the same numbers as
the document and the CLI.

Streamlit's script is simultaneously the input surface and the renderer, so this
module is both the view and the widget surface of the interactive flow. That
adaptation is recorded as decision L10 in the ODD feature document and must be
explained in the oral defense.
"""

from __future__ import annotations

import streamlit as st  # pyright: ignore[reportMissingImports]


# SPEC: S11, S15, S16 — the page Domenica's slice grows into the full resource.
def render() -> None:
    """Render the interactive resource page.

    The controls (λ/μ sliders, stability guard, run button, queue animation and
    the live theory-vs-simulation table) belong to Domenica Rojas's slice; the
    page currently renders the landing content so the documented command already
    starts without errors.
    """
    st.title("Simulación M/M/1 — APE 003")
    st.info(
        "Recurso interactivo en construcción. Aquí se presentarán los tres escenarios "
        "(λ = 2.0, 2.5 y 2.9 con μ = 3.0), las gráficas del comportamiento de la cola y "
        "de los tiempos de espera, y la comparación entre resultados teóricos y simulados."
    )
