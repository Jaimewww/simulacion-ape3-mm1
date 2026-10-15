"""Interactive Streamlit resource for the APE 003 M/M/1 practice.

Owner: Domenica Rojas.
Specs: S11 (interactive graphic resource), S15 (Streamlit as the chosen tool).

This file is the minimal landing page of the interactive resource. The controls
(scenario sliders, charts and comparison tables) are Domenica's slice and are
not implemented here yet.
"""

from __future__ import annotations

import streamlit as st  # pyright: ignore[reportMissingImports]


def main() -> None:
    """Render the Streamlit landing page."""
    st.title("Simulación M/M/1 — APE 003")
    st.info(
        "Recurso interactivo en construcción. Aquí se presentarán los tres escenarios "
        "(λ = 2.0, 2.5 y 2.9 con μ = 3.0), las gráficas del comportamiento de la cola y "
        "de los tiempos de espera, y la comparación entre resultados teóricos y simulados."
    )


if __name__ == "__main__":
    main()
