# Simulación de un sistema de líneas de espera M/M/1 mediante SimPy

Repositorio grupal de la **APE 003** de la asignatura **Simulación** (5.º ciclo,
FEIRNNR — Carrera de Computación). El paquete Python del proyecto implementa —de
forma incremental, por integrante— un modelo de colas **M/M/1** con **SimPy**, lo
compara contra las fórmulas teóricas y genera tablas, gráficas y un recurso
interactivo en **Streamlit**.

> Estado actual: **planificación y estructura base**. Los módulos del paquete son
> *stubs* con las firmas congeladas; la lógica, las gráficas y la app todavía no
> están implementadas. Las secciones que dependen de resultados indican
> explícitamente que están **pendientes**.

## Datos de la práctica

| Campo | Detalle |
| --- | --- |
| Asignatura | Simulación |
| Ciclo | 5.º ciclo — FEIRNNR, Carrera de Computación |
| Práctica | Nro. 03 — APE 003 |
| Título | Simulación de un sistema de líneas de espera M/M/1 mediante SimPy |
| Docente | José O. Guamán Q. |
| Integrantes | Jaime Landazuri, Richard Chamba, Cael Soto, Domenica Rojas |
| Recurso interactivo | Aplicación **Streamlit** |
| Sistema operativo objetivo | Linux o macOS |

## Objetivo

> Simular un sistema de líneas de espera M/M/1 utilizando Python y SimPy,
> analizando el comportamiento de los clientes, la cola y el servidor.

De forma específica, la práctica busca:

- Implementar un modelo M/M/1 utilizando la biblioteca SimPy.
- Calcular las principales métricas teóricas del sistema de espera.
- Comparar los resultados teóricos con los obtenidos mediante la simulación.

## Modelo teórico

El modelo M/M/1 representa un sistema de líneas de espera con:

- Llegadas de clientes siguiendo una **distribución de Poisson** (tasa `λ`).
- Tiempos de servicio con **distribución exponencial** (tasa `μ`).
- **Un único servidor**.
- Atención de clientes bajo el principio **FIFO**: primero en llegar, primero en
  ser atendido.

Parámetros principales:

- `λ`: tasa promedio de llegada de clientes.
- `μ`: tasa promedio de servicio del servidor.
- `ρ` (*rho*): utilización del servidor.

Para que el sistema sea **estable** debe cumplirse:

```text
λ < μ
```

Las principales medidas teóricas del sistema son:

| Medida | Significado | Fórmula |
| --- | --- | --- |
| `ρ` | Utilización del servidor | `ρ = λ / μ` |
| `L` | Número promedio de clientes en el sistema | `L = λ / (μ − λ)` |
| `Lq` | Número promedio de clientes en la cola | `Lq = λ² / (μ (μ − λ))` |
| `W` | Tiempo promedio en el sistema | `W = 1 / (μ − λ)` |
| `Wq` | Tiempo promedio de espera en la cola | `Wq = λ / (μ (μ − λ))` |

> **Nota sobre `ρ`.** El texto de la guía (sección 5.1) imprime `ρ = μ / λ`, pero
> esa relación contradice la propia condición de estabilidad `λ < μ` de la misma
> sección. La implementación usa `ρ = λ / μ`, que es la definición correcta de
> utilización para un servidor y la única compatible con `λ < μ`; además coincide
> con el pseudocódigo de la guía, que calcula `ρ = λ / μ`. Esta desviación queda
> documentada aquí y en el plan SDD del proyecto.

## Escenarios

La guía define tres escenarios; en todos ellos `μ = 3.0`.

| Escenario | λ | μ | Condición |
| --- | --- | --- | --- |
| 1 | 2.0 | 3.0 | Sistema estable |
| 2 | 2.5 | 3.0 | Mayor utilización |
| 3 | 2.9 | 3.0 | Cerca de saturación |

Para cada escenario se registran `ρ`, `L`, `Lq`, `W` y `Wq`, además del tiempo
promedio de espera simulado y el tamaño promedio de la cola simulado, y luego se
comparan los resultados teóricos y simulados mediante una tabla. **Los valores
teóricos y simulados aún no se han generado** (ver *Entregables*).

## Estructura del proyecto

```text
.
├── app/
│   └── streamlit_app.py      # Recurso interactivo (Streamlit) — Domenica Rojas
├── docs/
│   ├── guia/                 # Guía firmada APE 003 (PDF + extracción de texto)
│   └── division-trabajo.md   # Reparto de trabajo del equipo
├── openspec/                 # Plan SDD: propuesta, specs, diseño y tareas
│   └── changes/ape3-mm1-queue-simulation/
├── odd/                      # Seguimiento ODD (ignorado por git)
│   └── tasks/ape3-mm1-queue-simulation.md
├── outputs/                  # Artefactos generados: CSV, PNG (ignorado por git)
├── reports/
│   └── README.md             # Qué va en reports/ y regla de artefactos
├── src/
│   └── mm1/                  # Paquete Python (instalable)
│       ├── __init__.py       # API pública congelada (re-exportaciones)
│       ├── metrics.py        # Métricas teóricas — Richard Chamba
│       ├── simulation.py     # Núcleo SimPy — Jaime Landazuri
│       ├── scenarios.py      # Catálogo y ejecución de escenarios — Richard Chamba
│       ├── analysis.py       # Agregación y comparación — Richard Chamba
│       ├── tables.py         # Tabla comparativa (CSV/LaTeX) — Cael Soto
│       ├── charts.py         # Gráficas (Matplotlib) — Cael Soto
│       └── cli.py            # Punto de entrada por línea de comandos — Jaime Landazuri
├── tests/
│   └── test_smoke.py         # Prueba estructural del andamiaje (única prueba base)
├── .gitignore
├── pyproject.toml            # Empaquetado, ruff y configuración de pytest
├── requirements.txt          # Dependencias (runtime + desarrollo)
└── README.md
```

> `odd/` contiene el seguimiento local del flujo ODD y **no se versiona**;
> `openspec/` sí se versiona. Los artefactos generados (CSV, PNG, LaTeX) se
> escriben en `outputs/` y se ignoran en git.

## Requisitos e instalación

Requisitos:

- **Python 3.10 o superior** (definido en `pyproject.toml`). La guía solo pide
  Python 3.x; el proyecto fija `>=3.10` para las anotaciones de tipo modernas.
- Linux o macOS.

Instalación en un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` es la fuente plana de dependencias y se mantiene en sincronía
con `[project].dependencies` de `pyproject.toml`. No hay versiones fijadas
(*pins*) a propósito, porque cada integrante trabaja en una máquina distinta.

## Cómo ejecutar

### Recurso interactivo (Streamlit)

```bash
streamlit run app/streamlit_app.py
```

La app es la página de aterrizaje del recurso interactivo. Los controles
(deslizadores, gráficas interactivas y tablas) todavía están **pendientes**: son
parte del entregable de Domenica Rojas.

### Línea de comandos (CLI)

El plan SDD prevé una única entrada de orquestación a nivel de repositorio:

```bash
python -m mm1
```

**La CLI todavía no está implementada.** `src/mm1/cli.py` solo contiene el *stub*
de `main`; su lógica y sus opciones se definen en el plan SDD (ver *Enlaces
útiles*) y aún no se han escrito. Por ahora este comando no produce resultados.

> El paquete usa una disposición `src/`. Para ejecutarlo sin instalarlo, activa el
> entorno virtual e instálalo en modo editable (`pip install -e .`) o exporta
> `PYTHONPATH=src`.

## Cómo ejecutar los tests

Con el entorno virtual activado:

```bash
pytest
```

La configuración en `pyproject.toml` busca las pruebas en `tests/` y agrega `src/`
al *path* de importación, por lo que `pytest` funciona desde la raíz del
repositorio. En el andamiaje solo existe `tests/test_smoke.py` (prueba
estructural). Cada integrante agrega sus propias pruebas de comportamiento
primero (enfoque *test-first*) en su archivo correspondiente.

## Reparto de trabajo

| Integrante | Archivos o entregables |
| --- | --- |
| Jaime Landazuri | `src/mm1/simulation.py`, `src/mm1/cli.py` |
| Richard Chamba | `src/mm1/metrics.py`, `src/mm1/scenarios.py`, `src/mm1/analysis.py` |
| Cael Soto | `src/mm1/tables.py`, `src/mm1/charts.py` |
| Domenica Rojas | `app/streamlit_app.py`, `reports/**` |

El detalle de tareas, dependencias y criterios de aceptación está en
[`docs/division-trabajo.md`](docs/division-trabajo.md).

## Entregables de la práctica

| Entregable | Estado |
| --- | --- |
| Código del modelo M/M/1 en SimPy (`src/mm1/`) | **Pendiente** (stubs con firmas congeladas) |
| Gráficas del comportamiento de la cola y de los tiempos de espera | **Pendiente** (`charts.py`) |
| Tabla comparativa teórico vs. simulado | **Pendiente** (`tables.py`, `analysis.py`) |
| Documento técnico | **Pendiente** (`reports/`) |
| Video de demostración | **Pendiente** (`reports/`) |
| Recurso interactivo (Streamlit) | **Pendiente** (`app/streamlit_app.py`) |
| Defensa oral y demostración | **Pendiente** |

No se incluyen resultados numéricos porque la simulación **aún no se ha
ejecutado**: no hay valores teóricos ni simulados que reportar.

## Enlaces útiles

- Guía de la práctica: [`docs/guia/ape3_guia_simulacion_semana3.pdf`](docs/guia/ape3_guia_simulacion_semana3.pdf)
  y su extracción de texto [`docs/guia/ape3_guia_simulacion_semana3.txt`](docs/guia/ape3_guia_simulacion_semana3.txt).
- Plan SDD (propuesta, especificaciones, diseño y tareas):
  [`openspec/changes/ape3-mm1-queue-simulation/`](openspec/changes/ape3-mm1-queue-simulation/).
- Reparto de trabajo: [`docs/division-trabajo.md`](docs/division-trabajo.md).
- Documento técnico y figuras: [`reports/`](reports/).

## Uso de IA y probidad académica

Este proyecto se apoya en asistentes de IA para planificar, generar andamiaje y
revisar código, siempre bajo supervisión humana. Cada integrante entiende,
verifica y defiende el código de su parte; los resultados se reproducen con
comandos explícitos y las decisiones de diseño quedan registradas en el plan SDD.
El uso de IA se documenta de forma honesta para cumplir con los principios de
solidaridad, transparencia, responsabilidad y honestidad de la práctica.
