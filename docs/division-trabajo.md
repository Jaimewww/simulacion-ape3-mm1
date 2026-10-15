# División del trabajo — APE 003: Simulación M/M/1 con SimPy

**Asignatura:** Simulación (5.º ciclo) · **Práctica:** 003
**Título:** Simulación de un sistema de líneas de espera M/M/1 mediante SimPy
**Integrantes:** Jaime Landazuri, Richard Chamba, Cael Soto, Domenica Rojas
**Documento fuente:** `docs/guia/ape3_guia_simulacion_semana3.txt` (guía firmada, §1–§10)
**Plan técnico:** `openspec/changes/ape3-mm1-queue-simulation/{proposal,design,tasks}.md`

---

## 1. Objetivo del documento

Repartir la práctica en cuatro bloques de trabajo independientes, de modo que cada
integrante pueda avanzar con un agente de IA sin pisar los archivos de otro, y que
todo lo evaluado en la guía (defensa, implementación y documento) quede cubierto.

La guía califica tres criterios: **Defensa oral y demostración (4/10)**,
**Implementación (3/10)** y **Documento (3/10)**. Los bloques 2, 3 y 4 producen la
implementación; el bloque 5 produce el recurso interactivo y el documento; el
bloque 1 habilita a los demás.

---

## 2. Resumen de bloques

| # | Integrante | Rol en la práctica | Archivos propios | Specs | Rama |
|---|-----------|--------------------|------------------|-------|------|
| 1 | Orquestador (cualquier integrante) | Base del repositorio y empaquetado | `requirements.txt`, `pyproject.toml`, `.gitignore`, `README.md`, `src/mm1/__init__.py`, `src/mm1/__main__.py` | S2, S10, S12 | `feat/orchestrator-foundation` |
| 2 | Jaime Landazuri | Motor de simulación SimPy y línea de comandos | `src/mm1/simulation.py`, `src/mm1/cli.py`, `tests/test_simulation.py`, `tests/test_smoke.py` | S4, S7, S12, S13 | `feat/jaime-simulation-cli` |
| 3 | Richard Chamba | Modelo teórico, escenarios y análisis estadístico | `src/mm1/metrics.py`, `src/mm1/scenarios.py`, `src/mm1/analysis.py`, `tests/test_metrics.py`, `tests/test_scenarios.py`, `tests/test_analysis.py` | S3, S5, S6 | `feat/richard-theory-analysis` |
| 4 | Cael Soto | Tabla comparativa y gráficas | `src/mm1/tables.py`, `src/mm1/charts.py`, `tests/test_tables.py`, `tests/test_charts.py`, `reports/figures/**` | S6, S7 | `feat/cael-tables-charts` |
| 5 | Domenica Rojas | Recurso interactivo y documento técnico | `app/streamlit_app.py`, `tests/test_app.py`, `reports/**` | S8, S9, S11, S15 | `feat/domenica-streamlit-document` |

Regla de oro: **nadie escribe en los archivos de otro bloque**. Las interfaces
públicas están congeladas en `design.md`; si alguien necesita un cambio de firma,
se avisa al equipo antes de tocar código.

---

## 3. Reglas comunes

1. **Un bloque = un Pull Request** hacia `main`, con su código, sus pruebas y la
   documentación que ese cambio invalide.
2. **TDD estricto:** primero la prueba que falla (RED), luego la implementación
   mínima (GREEN), después una prueba que conserva el comportamiento anterior
   (PRESERVE) y al final la limpieza (REFACTOR). Los tests viven en `tests/`.
3. **Comandos oficiales del proyecto:**
   - Pruebas enfocadas: `python -m pytest tests/test_<modulo>.py -q`
   - Pruebas completas: `python -m pytest -q`
   - Estilo: `python -m ruff check src tests app`
   - Demostración / regeneración de resultados: `python -m mm1 --out outputs/`
   - Recurso interactivo: `streamlit run app/streamlit_app.py`
4. **`outputs/` no se versiona:** los CSV y PNG se regeneran con el comando de
   demostración. Las figuras que van al documento se copian a `reports/figures/`.
5. **Decisión técnica obligatoria:** la guía §5.1 imprime `ρ = μ / λ`, pero su
   propia condición de estabilidad es `λ < μ`. Se implementa **`ρ = λ / μ`** y la
   desviación se documenta (decisión D1 en `design.md`). No cambiar esta decisión
   sin acuerdo del equipo.
6. **Escenarios fijos de la guía:** (λ=2.0, μ=3.0) estable, (λ=2.5, μ=3.0) mayor
   utilización, (λ=2.9, μ=3.0) cerca de saturación.

---

## 4. Bloque 1 — Base del repositorio (Orquestador)

**Archivos propios:** `requirements.txt`, `pyproject.toml`, `.gitignore`,
`README.md`, `src/mm1/__init__.py`, `src/mm1/__main__.py`.
**Specs:** S2 (stack), S10 (estructura y README), S12 (Python).

**Entregables**

- Dependencias fijadas: SimPy, NumPy, Matplotlib, pandas, Streamlit, pytest,
  pytest-cov, ruff.
- `pyproject.toml` con layout `src/`, configuración de pytest y ruff.
- `src/mm1/__init__.py` que reexporta la interfaz pública congelada.
- `src/mm1/__main__.py` que permite `python -m mm1` (decisión D11).
- `.gitignore` con `outputs/` y `.atl/`.

**Criterios de aceptación**

- `python -m pip install -r requirements.txt` termina sin errores.
- `python -c "import mm1"` termina sin errores.
- `python -m ruff check src` no reporta hallazgos.
- `python -m mm1 --help` funciona cuando el bloque 2 ya está integrado.

**Prerrequisitos:** ninguno. **Bloquea a:** bloques 2, 3, 4 y 5.

**Rama y PR:** `feat/orchestrator-foundation` → PR a `main`.

---

## 5. Bloque 2 — Motor de simulación y CLI (Jaime Landazuri)

**Archivos propios:** `src/mm1/simulation.py`, `src/mm1/cli.py`,
`tests/test_simulation.py`, `tests/test_smoke.py`.
**Specs:** S4 (pseudocódigo de la guía), S7 (resultados esperados),
S12 (Python), S13 (alcance de la planificación).

**Interfaz que debe cumplir**

```python
def run_mm1(lam: float, mu: float, sim_time: float = 1000.0,
            seed: int | None = None, scenario: int = 0,
            warmup: float = 0.0) -> ScenarioRun

def main(argv: Sequence[str] | None = None) -> int   # python -m mm1
```

`ScenarioRun` y `CustomerRecord` son dataclasses congeladas definidas en
`design.md`. Internamente: entorno SimPy, servidor con `capacidad = 1`, llegadas y
servicios exponenciales, atención FIFO, registro de tiempos de espera y de
tamaños de cola.

**Entregables**

- Simulación M/M/1 funcional con un único servidor y FIFO.
- Guarda de estabilidad: si `λ >= μ` no se simula y se imprime exactamente
  `El sistema no es estable`.
- CLI con `--lam --mu --scenarios --replications --sim-time --seed --warmup --out`.
- `tests/test_smoke.py` con el flujo mínimo de extremo a extremo de la CLI.

**Criterios de aceptación**

- `python -m pytest tests/test_simulation.py tests/test_smoke.py -q` pasa.
- `python -m mm1 --replications 5 --sim-time 300 --out outputs/` termina con
  código 0 y produce archivos en `outputs/`.
- `main(["--lam", "3.0", "--mu", "3.0"])` devuelve código distinto de cero,
  imprime `El sistema no es estable` y no escribe archivos.
- Dos ejecuciones con la misma semilla dan clientes y métricas idénticos.

**Prerrequisitos:** bloque 1. **Lo consumen:** bloques 3 (escenarios), 4 (tablas y
gráficas) y 5 (recurso interactivo).

**Rama y PR:** `feat/jaime-simulation-cli` → PR a `main`.

---

## 6. Bloque 3 — Modelo teórico, escenarios y análisis (Richard Chamba)

**Archivos propios:** `src/mm1/metrics.py`, `src/mm1/scenarios.py`,
`src/mm1/analysis.py`, `tests/test_metrics.py`, `tests/test_scenarios.py`,
`tests/test_analysis.py`.
**Specs:** S3 (modelo teórico), S5 (escenarios), S6 (métricas y tabla).

**Interfaz que debe cumplir**

```python
def utilization(lam: float, mu: float) -> float
def is_stable(lam: float, mu: float) -> bool
def theoretical_metrics(lam: float, mu: float) -> TheoryMetrics

SCENARIOS: tuple[Scenario, ...]
def run_scenarios(replications: int = 30, sim_time: float = 1000.0,
                  base_seed: int = 42, warmup: float = 0.0) -> list[ScenarioRun]

def confidence_interval(values, confidence: float = 0.95) -> tuple[float, float]
def relative_error(simulated: float, theoretical: float) -> float
def summarize(runs) -> list[ScenarioSummary]
```

**Entregables**

- `rho = lam / mu`, `L = lam/(mu-lam)`, `Lq = lam²/(mu(mu-lam))`,
  `W = 1/(mu-lam)`, `Wq = lam/(mu(mu-lam))` y la guarda `lam >= mu`.
- `SCENARIOS` con los tres pares (λ, μ) de la guía, ids 1..3 y sus condiciones
  textuales.
- `run_scenarios` con semillas reproducibles derivadas de `base_seed` y de la
  réplica.
- `summarize` con media simulada, desviación estándar, intervalo de confianza al
  95 % y error relativo frente a la teoría, para `L`, `Lq`, `W` y `Wq`.

**Criterios de aceptación**

- `python -m pytest tests/test_metrics.py tests/test_scenarios.py tests/test_analysis.py -q` pasa.
- Para (2.0, 3.0): `L = 2.0`, `Lq = 1.3333…`, `W = 1.0`, `Wq = 0.6666…`.
- Para (2.5, 3.0): `L = 5.0`, `W = 2.0`. Para (2.9, 3.0): `L = 29.0`, `W = 10.0`.
- `theoretical_metrics(3.0, 3.0)` lanza `ValueError`.
- `run_scenarios(replications=3, sim_time=100.0)` devuelve 9 corridas agrupadas
  por escenario.

**Prerrequisitos:** bloque 1 para `metrics.py`; bloque 2 para `scenarios.py` y
`analysis.py` (necesitan `run_mm1`). **Lo consumen:** bloques 4 y 5.

**Rama y PR:** `feat/richard-theory-analysis` → PR a `main` (dos PR si se separa
la parte teórica de la parte de escenarios y análisis).

---

## 7. Bloque 4 — Tabla comparativa y gráficas (Cael Soto)

**Archivos propios:** `src/mm1/tables.py`, `src/mm1/charts.py`,
`tests/test_tables.py`, `tests/test_charts.py`, `reports/figures/**`.
**Specs:** S6 (tabla comparativa), S7 (gráficas del comportamiento).

**Interfaz que debe cumplir**

```python
def comparison_dataframe(summaries) -> "pandas.DataFrame"
def write_csv(df, path) -> Path
def to_latex(df, path) -> Path

def plot_queue_evolution(run, path) -> Path
def plot_wait_times(run, path) -> Path
def plot_theory_vs_sim(summaries, path) -> Path
def plot_scenario_comparison(summaries, path) -> Path
def generate_all(runs, summaries, out_dir) -> list[Path]
```

La tabla debe incluir, por escenario: `ρ`, `L`, `Lq`, `W`, `Wq`, tiempo promedio
de espera simulado, tamaño promedio de cola simulado, desviación estándar,
intervalo de confianza al 95 % y errores relativos; una fila por escenario, en
orden 1, 2, 3.

**Entregables**

- Tabla comparativa exportable a CSV y a LaTeX (para el documento).
- Cuatro gráficas: evolución de la cola, tiempos de espera, teoría vs simulación
  y comparación entre escenarios.
- Figuras definitivas copiadas a `reports/figures/`.

**Criterios de aceptación**

- `python -m pytest tests/test_tables.py tests/test_charts.py -q` pasa.
- `python -m mm1 --replications 5 --sim-time 300 --out outputs/` produce el CSV,
  el `.tex` y los PNG; todos existen y no están vacíos.
- El backend `Agg` está forzado: las gráficas se generan sin pantalla.
- Los tests verifican existencia, tipo y firma PNG; nunca comparan píxeles.

**Prerrequisitos:** bloques 1, 2 y 3. **Lo consume:** bloque 5 (documento).

**Rama y PR:** `feat/cael-tables-charts` → PR a `main`.

---

## 8. Bloque 5 — Recurso interactivo y documento (Domenica Rojas)

**Archivos propios:** `app/streamlit_app.py`, `tests/test_app.py`, `reports/**`.
**Specs:** S8 (10 preguntas de control), S9 (criterios de evaluación),
S11 (recurso gráfico interactivo), S15 (Streamlit).

**Interfaz que debe cumplir (helpers puros, sin abrir Streamlit)**

```python
def theory_row(lam: float, mu: float) -> dict[str, float]
def stability_message(lam: float, mu: float) -> str
def scenario_table(summaries) -> "pandas.DataFrame"
def build_queue_figure(run) -> "matplotlib.figure.Figure"
def build_comparison_figure(summaries) -> "matplotlib.figure.Figure"
```

**Entregables — recurso interactivo (Streamlit)**

- Deslizadores para λ y μ.
- Panel de `ρ` con aviso de estabilidad (bloquea la ejecución si `λ >= μ`).
- Botón para ejecutar la simulación.
- Animación de la evolución de la cola a partir de `queue_trace`.
- Tabla en vivo que compara teoría y simulación.
- Al menos dos gráficas interactivas sobre los tres escenarios.
- Verificación manual: `streamlit run app/streamlit_app.py`.

**Entregables — documento técnico (`reports/`)**

- Estructura y presentación: título, objetivos, modelo matemático con la nota de
  la decisión D1, procedimiento y escenarios.
- Procedimiento y resultados con evidencias: tabla comparativa, figuras y el
  comando `python -m mm1 --out outputs/` que las reproduce.
- Respuestas a las **10 preguntas de control** de la guía §7, cada una con la
  evidencia simulada que la respalda.
- Conclusiones relacionadas con los tres objetivos de la práctica y con el
  comportamiento esperado de la guía §6 (el tiempo de espera y la cola crecen
  cuando λ se acerca a μ).
- Enlace al **video de demostración** y notas para la defensa oral.

**Criterios de aceptación**

- `python -m pytest tests/test_app.py -q` pasa.
- `streamlit run app/streamlit_app.py` arranca sin errores de importación.
- Con λ = 3.0 y μ = 3.0 la aplicación muestra el bloqueo de estabilidad y no
  ejecuta la simulación.
- Las 10 preguntas están numeradas y respondidas; tres de ellas citadas
  textualmente desde la guía.
- Cada figura citada por el documento existe en `reports/figures/`.

**Prerrequisitos:** bloques 1, 2, 3 y 4 (usa sus funciones y sus figuras).

**Rama y PR:** `feat/domenica-streamlit-document` → PR a `main`.

---

## 9. Orden de integración

| Orden | Rama | Depende de | Resultado verificable |
|-------|------|-----------|------------------------|
| 1 | `feat/orchestrator-foundation` | — | `python -c "import mm1"` |
| 2 | `feat/richard-theory-analysis` (parte teórica) | 1 | `python -m pytest tests/test_metrics.py -q` |
| 3 | `feat/jaime-simulation-cli` | 1, 2 | `python -m mm1 --replications 5 --sim-time 300 --out outputs/` |
| 4 | `feat/richard-theory-analysis` (escenarios y análisis) | 3 | `python -m pytest tests/test_scenarios.py tests/test_analysis.py -q` |
| 5 | `feat/cael-tables-charts` | 4 | CSV, TeX y PNG en `outputs/` |
| 6 | `feat/domenica-streamlit-document` | 5 | `streamlit run app/streamlit_app.py` y documento en `reports/` |

Los bloques se pueden **programar en paralelo** porque los archivos son disjuntos,
pero la integración sigue este orden: cada PR necesita que existan las interfaces
congeladas del anterior. Todos los PR apuntan a `main` y ninguno debe superar las
400 líneas escritas; si un bloque las supera, se divide en dos PR del mismo
integrante.

---

## 10. Cómo trabajar con agentes de IA

### 10.1 Reglas generales

1. Entrega al agente **una sola tarea** del archivo
   `openspec/changes/ape3-mm1-queue-simulation/tasks.md`.
2. Declara explícitamente los **archivos permitidos** de tu bloque y prohíbe el
   resto.
3. Exige evidencia ejecutada: la salida real de los comandos, no descripciones.
4. El agente **no** hace `git add`, `git commit`, `git push` ni crea ramas; eso lo
   haces tú al revisar la evidencia.
5. Si el agente necesita cambiar una firma pública, debe detenerse y avisar: la
   interfaz está congelada en `design.md`.
6. Conserva los archivos ajenos: si `git status` muestra cambios de otro bloque,
   no se incluyen en tu PR.

### 10.2 Prompts por bloque

**Bloque 1 — base (orquestador)**

```text
Tarea: ejecuta las tareas 1.1 a 1.4 de
openspec/changes/ape3-mm1-queue-simulation/tasks.md.
Archivos permitidos: requirements.txt, pyproject.toml, .gitignore, README.md,
src/mm1/__init__.py, src/mm1/__main__.py.
Interfaz: copia exactamente la interfaz pública de design.md.
No toques src/mm1/metrics.py, simulation.py, scenarios.py, analysis.py,
tables.py, charts.py, cli.py, app/ ni tests/.
Evidencia obligatoria: salida de "python -m pip install -r requirements.txt",
"python -c \"import mm1\"", "python -m ruff check src" y "git status --short".
```

**Bloque 2 — simulación y CLI (Jaime)**

```text
Tarea: ejecuta las tareas del bloque 2 (3.1 a 3.6) de tasks.md.
Archivos permitidos: src/mm1/simulation.py, src/mm1/cli.py,
tests/test_simulation.py, tests/test_smoke.py.
Interfaz: run_mm1 y main con las firmas exactas de design.md.
No toques metrics.py, scenarios.py, analysis.py, tables.py, charts.py, app/.
Trabaja en TDD: escribe tests/test_simulation.py primero y muestra que falla,
luego implementa y muestra que pasa.
Evidencia obligatoria: salida de "python -m pytest tests/test_simulation.py -q",
"python -m pytest tests/test_smoke.py -q" y
"python -m mm1 --replications 5 --sim-time 300 --out outputs/".
```

**Bloque 3 — teoría, escenarios y análisis (Richard)**

```text
Tarea: ejecuta las tareas del bloque 3 (2.1 a 2.4, 4.1 a 4.5) de tasks.md.
Archivos permitidos: src/mm1/metrics.py, src/mm1/scenarios.py,
src/mm1/analysis.py, tests/test_metrics.py, tests/test_scenarios.py,
tests/test_analysis.py.
Interfaz: firmas exactas de design.md.
Usa rho = lam / mu (decisión D1); no uses la fórmula impresa en la guía §5.1.
No toques simulation.py, cli.py, tables.py, charts.py, app/, reports/.
Evidencia obligatoria: salida de
"python -m pytest tests/test_metrics.py tests/test_scenarios.py tests/test_analysis.py -q"
con los valores analíticos L, Lq, W y Wq de los tres escenarios.
```

**Bloque 4 — tablas y gráficas (Cael)**

```text
Tarea: ejecuta las tareas del bloque 4 (5.1 a 5.5) de tasks.md.
Archivos permitidos: src/mm1/tables.py, src/mm1/charts.py,
tests/test_tables.py, tests/test_charts.py, reports/figures/.
Interfaz: firmas exactas de design.md; usa matplotlib con backend Agg.
No toques metrics.py, simulation.py, scenarios.py, analysis.py, cli.py, app/.
Evidencia obligatoria: salida de
"python -m pytest tests/test_tables.py tests/test_charts.py -q" y el listado
de archivos generados por "python -m mm1 --replications 5 --sim-time 300 --out outputs/".
```

**Bloque 5 — recurso interactivo y documento (Domenica)**

```text
Tarea: ejecuta las tareas del bloque 5 (6.1 a 6.8) de tasks.md.
Archivos permitidos: app/streamlit_app.py, tests/test_app.py, reports/**.
Interfaz: helpers puros con las firmas exactas de design.md.
El recurso debe tener deslizadores para λ y μ, aviso de estabilidad, botón de
ejecución, animación de la cola, tabla teoría vs simulación y al menos dos
gráficas interactivas.
El documento debe responder las 10 preguntas de control de la guía §7 e incluir
el enlace al video de demostración.
No toques src/mm1/ ni tests/ fuera de tests/test_app.py.
Evidencia obligatoria: salida de "python -m pytest tests/test_app.py -q",
confirmación de que "streamlit run app/streamlit_app.py" arranca, y la lista de
secciones y figuras del documento.
```

### 10.3 Evidencia obligatoria en cada entrega del agente

| Elemento | Ejemplo |
|----------|---------|
| Archivos modificados | `git status --short` con solo archivos del bloque |
| Prueba RED | Comando ejecutado y su salida fallida |
| Prueba GREEN | `python -m pytest tests/test_<modulo>.py -q` con el resumen final |
| Estilo | `python -m ruff check src tests app` sin hallazgos |
| Demostración | Salida de `python -m mm1 --out outputs/` o de `streamlit run` |
| Riesgos | Qué quedó pendiente y qué no se pudo verificar |

---

## 11. Criterios de evaluación y responsables

| Criterio de la guía §8 | Peso | Responsables |
|------------------------|------|--------------|
| Defensa oral y demostración | 4/10 | Todos; Jaime explica el motor y la CLI, Richard el modelo matemático, Cael las gráficas, Domenica el recurso interactivo y el documento |
| Implementación | 3/10 | Jaime (motor y CLI), Richard (teoría, escenarios, análisis), Cael (tablas y gráficas) |
| Documento | 3/10 | Domenica (estructura, resultados, 10 preguntas, conclusiones, video), con evidencias de Cael |

**Video de demostración:** lo graba Domenica con la participación de cada
integrante en su bloque, mostrando `python -m mm1 --out outputs/` y el recurso
interactivo.
