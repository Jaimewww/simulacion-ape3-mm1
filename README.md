# Simulación de un sistema de líneas de espera M/M/1 mediante SimPy

Repositorio grupal de la **APE 003** de la asignatura **Simulación** (5.º ciclo,
FEIRNNR — Carrera de Computación). El paquete Python del proyecto implementa —de
forma incremental, por integrante— un modelo de colas **M/M/1** con **SimPy**, lo
compara contra las fórmulas teóricas y genera tablas, gráficas y un recurso
interactivo en **Streamlit**.

> Estado actual: **estructura base y modelo teórico completos**. Richard Chamba
> implementó `ρ`, `L`, `Lq`, `W`, `Wq` y la guarda de estabilidad, con 17 pruebas
> de teoría. El motor de simulación, los escenarios, el análisis, las gráficas
> y la app interactiva siguen **pendientes**.

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
comparan los resultados teóricos y simulados mediante una tabla. El modelo teórico
ya está implementado; los resultados simulados y su comparación siguen pendientes.

| λ | μ | ρ | L | Lq | W | Wq |
| --- | --- | --- | --- | --- | --- | --- |
| 2.0 | 3.0 | 0.666667 | 2.0 | 1.333333 | 1.0 | 0.666667 |
| 2.5 | 3.0 | 0.833333 | 5.0 | 4.166667 | 2.0 | 1.666667 |
| 2.9 | 3.0 | 0.966667 | 29.0 | 28.033333 | 10.0 | 9.666667 |

Valores teóricos redondeados a seis decimales cuando corresponde.

## Estructura del proyecto

```text
.
├── app/
│   └── streamlit_app.py        # Entrada fina del recurso interactivo — Domenica Rojas
├── docs/
│   ├── guia/                   # Guía firmada APE 003 (PDF + extracción de texto)
│   └── division-trabajo.md     # Reparto de trabajo del equipo
├── openspec/                   # Plan SDD: propuesta, specs, diseño y tareas
│   └── changes/ape3-mm1-queue-simulation/
├── odd/                        # Seguimiento ODD (ignorado por git)
│   └── tasks/ape3-mm1-queue-simulation.md
├── outputs/                    # Artefactos generados: CSV, PNG (ignorado por git)
├── reports/
│   └── README.md               # Qué va en reports/ y regla de artefactos
├── src/
│   └── mm1/                    # Paquete Python (instalable), en tres capas MVC
│       ├── __init__.py         # API pública congelada (25 nombres)
│       ├── __main__.py         # Entrada de `python -m mm1`
│       ├── model/              # CAPA MODELO: el dominio, sin render ni I/O
│       │   ├── metrics.py      # Métricas teóricas — Richard Chamba
│       │   ├── simulation.py   # Núcleo SimPy — Jaime Landazuri
│       │   ├── scenarios.py    # Catálogo y ejecución de escenarios — Richard Chamba
│       │   └── analysis.py     # Agregación, IC 95 % y error relativo — Richard Chamba
│       ├── view/               # CAPA VISTA: presenta, no calcula
│       │   ├── tables.py       # Tabla comparativa (CSV/LaTeX) — Cael Soto
│       │   ├── charts.py       # Gráficas (Matplotlib) — Cael Soto
│       │   └── streamlit_view.py  # Página interactiva — Domenica Rojas
│       └── controller/         # CAPA CONTROLADOR: orquesta las otras dos
│           ├── study.py        # run_study, servicio compartido — Richard Chamba
│           └── cli.py          # Punto de entrada por línea de comandos — Jaime Landazuri
├── tests/
│   └── test_smoke.py           # Prueba estructural del andamiaje (única prueba base)
├── .gitignore
├── CONTRIBUTING.md             # Orden de aportes y reglas de trabajo del equipo
├── pyproject.toml              # Empaquetado, ruff y configuración de pytest
├── requirements.txt            # Dependencias (runtime + desarrollo)
└── README.md
```

> Estructura **MVC** (patrón de diseño pedido para el proyecto):
> `model/` tiene el dominio y no conoce la presentación; `view/` presenta y no calcula;
> `controller/` es la única capa que conoce a las otras dos.
> `view.streamlit_view` pide los resultados a `controller.run_study`, así la página
> interactiva y el documento muestran siempre los mismos números.
> `import mm1` **no** importa Streamlit: la página se carga solo cuando se abre la app.

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

La CLI tiene dos modos. `python -m mm1 --help` lista la superficie completa.

**Una corrida** (`--lam` y `--mu`). Corre una sola simulación y muestra los valores
simulados junto a los teóricos: es la prueba en vivo para la defensa oral y el modo
que ya funciona.

```bash
python -m mm1 --lam 2.0 --mu 3.0 --sim-time 2000 --seed 42
```

```text
Corrida única M/M/1   λ=2  μ=3  ρ_teórica=0.6667
métrica            teórica    simulada  error rel.
Wq                  0.6667      0.7048      5.73%
W                   1.0000      1.0336      3.36%
Lq                  1.3333      1.4003      5.02%
L                   2.0000      2.0533      2.67%
utilización         0.6667      0.6531      2.03%
clientes atendidos=3973  sim_time=2000  warmup=0  semilla=42
```

Si el sistema no es estable imprime `El sistema no es estable` y sale con código 2,
tal como pide la guía.

**Los tres escenarios de la guía** (modo por defecto). Corre el estudio completo y
exporta la tabla comparativa y las figuras a `--out`:

```bash
python -m mm1 --replications 30 --sim-time 1000 --out outputs/
```

> **Estado:** funciona de punta a punta. Sale 0 y escribe `comparacion.csv`,
> `comparacion.tex` y las figuras PNG en `--out` (por defecto `outputs/`). La CLI
> **no cambió una línea** cuando se integraron las etapas 7, 8 y 9: desde el primer
> día delegó en `controller.study.run_study` y en los renderizadores de `mm1.view`.

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
repositorio. Las pruebas están repartidas así: `tests/test_smoke.py` cubre la
estructura congelada y el comportamiento del CLI (38), `tests/test_metrics.py` la teoría
(17), `tests/test_simulation.py` el motor SimPy (23), `tests/test_scenarios.py` el
catálogo y las réplicas (9), `tests/test_analysis.py` la agregación con IC 95 % y error
relativo (58), `tests/test_study.py` el servicio compartido (5), y `tests/test_tables.py`
con `tests/test_charts.py` la tabla de 19 columnas, sus exports y las figuras (18 entre
los dos). En total **168 pruebas**. Cada integrante agrega sus pruebas primero (enfoque
*test-first*) en su archivo correspondiente.

## Reparto de trabajo

| Integrante | Capa MVC | Archivos o entregables |
| --- | --- | --- |
| Jaime Landazuri | Modelo + Controlador | `src/mm1/model/simulation.py`, `src/mm1/controller/cli.py`, `tests/test_simulation.py`, `tests/test_smoke.py` |
| Richard Chamba | Modelo + Controlador | `src/mm1/model/metrics.py`, `src/mm1/model/scenarios.py`, `src/mm1/model/analysis.py`, `src/mm1/controller/study.py`, `tests/test_metrics.py`, `tests/test_scenarios.py`, `tests/test_analysis.py`, `tests/test_study.py` |
| Cael Soto | Vista | `src/mm1/view/tables.py`, `src/mm1/view/charts.py`, `tests/test_tables.py`, `tests/test_charts.py`, `reports/figures/**` |
| Domenica Rojas | Vista + cierre | `src/mm1/view/streamlit_view.py`, `app/streamlit_app.py`, `tests/test_app.py`, `reports/ape3_mm1.tex`, `reports/ape3_mm1.pdf`, `reports/README.md`, `reports/assets/**` |

**El orden en que se hacen los aportes —de la base al recurso visual, que es el
entregable final del código— está en [`CONTRIBUTING.md`](CONTRIBUTING.md).** Ese es
el documento que hay que mirar para saber qué hacer ahora y qué todavía no.

El detalle de tareas, dependencias y criterios de aceptación está en
[`docs/division-trabajo.md`](docs/division-trabajo.md) y en el plan técnico
[`openspec/changes/ape3-mm1-queue-simulation/tasks.md`](openspec/changes/ape3-mm1-queue-simulation/tasks.md).

## Entregables de la práctica

| Entregable | Estado |
| --- | --- |
| Modelo teórico M/M/1 (`model/metrics.py`) | **✅ Listo** — Richard Chamba; 17 pruebas pasan |
| Motor M/M/1 en SimPy (`model/simulation.py`) | **✅ Listo** — Jaime Landazuri; 23 pruebas pasan y el motor es consistente contra la teoría |
| Los 3 escenarios de la guía con réplicas reproducibles (`model/scenarios.py`, `controller/study.py`) | **✅ Listo** — Richard Chamba; 30 réplicas por escenario y semillas derivadas de la base |
| Análisis de réplicas: IC 95 % de t de Student y error relativo (`model/analysis.py`) | **✅ Listo** — Richard Chamba; 58 pruebas |
| CLI completa (`python -m mm1 --lam … --mu …` y `--scenarios --out …`) | **✅ Listo** — Jaime Landazuri; los dos modos funcionan de punta a punta |
| Gráficas del comportamiento de la cola y de los tiempos de espera | **✅ Listo** — Cael Soto; en `reports/figures/` y regenerables con el CLI |
| Tabla comparativa teórico vs. simulado | **✅ Listo** — Cael Soto; 19 columnas con IC 95 % y error relativo, exportada a `comparacion.csv` y `comparacion.tex` |
| Documento técnico | **Pendiente** (`reports/`) |
| Video de demostración | **Pendiente** (`reports/`) |
| Recurso interactivo (Streamlit) | **Pendiente** (`src/mm1/view/streamlit_view.py` + entrada `app/streamlit_app.py`) |
| Defensa oral y demostración | **Pendiente** |

Los valores teóricos aparecen en la sección *Escenarios*. El motor ya corre: la CLI
de una corrida compara teoría y simulación en vivo. Lo que sigue pendiente son los
resultados definitivos del documento (tabla comparativa y figuras del reporte), que
dependen de las etapas 5 a 9, y por eso no se incluyen números aquí.

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
