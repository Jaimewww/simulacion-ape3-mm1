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
implementación; el bloque 5 produce la animación de la cola y el documento; el
bloque 1 habilita a los demás.

---

## 2. Resumen de bloques

| # | Integrante | Rol en la práctica | Archivos propios | Specs | Rama |
|---|-----------|--------------------|------------------|-------|------|
| 1 | Orquestador (cualquier integrante) | Base del repositorio, estructura MVC y empaquetado | `requirements.txt`, `pyproject.toml`, `.gitignore`, `README.md`, `CONTRIBUTING.md`, `src/mm1/__init__.py`, `src/mm1/__main__.py`, `src/mm1/model/__init__.py`, `src/mm1/view/__init__.py`, `src/mm1/controller/__init__.py` | S2, S10, S12, S16, S17 | `feat/orchestrator-foundation` |
| 2 | Jaime Landazuri | Motor de simulación SimPy y línea de comandos | `src/mm1/model/simulation.py`, `src/mm1/controller/cli.py`, `tests/test_simulation.py`, `tests/test_smoke.py` | S4, S7, S12, S13 | `feat/jaime-simulation-cli` |
| 3 | Richard Chamba | Modelo teórico, escenarios, análisis estadístico y servicio de estudio | `src/mm1/model/metrics.py`, `src/mm1/model/scenarios.py`, `src/mm1/model/analysis.py`, `src/mm1/controller/study.py`, `tests/test_metrics.py`, `tests/test_scenarios.py`, `tests/test_analysis.py`, `tests/test_study.py` | S3, S5, S6, S16 | `feat/richard-theory-analysis` |
| 4 | Cael Soto | Tabla comparativa y gráficas | `src/mm1/view/tables.py`, `src/mm1/view/charts.py`, `tests/test_tables.py`, `tests/test_charts.py`, `reports/figures/**` | S6, S7 | `feat/cael-tables-charts` |
| 5 | Domenica Rojas | Animación de la cola y documento técnico | `src/mm1/view/animation.py`, `tests/test_animation.py`, `reports/ape3_mm1.tex`, `reports/ape3_mm1.pdf`, `reports/README.md`, `reports/assets/**` | S8, S9, S19, S20 | `domenica-rojas` |

**El orden en que se hacen los aportes (de la base al recurso visual, que es el
entregable final del código) está en
[`../CONTRIBUTING.md`](../CONTRIBUTING.md).** Este documento lo detalla por
integrante; ante cualquier duda de "qué va ahora y qué todavía no", manda el orden
de `CONTRIBUTING.md`.

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
   - Animación de la cola: `python -m mm1 --lam 2.0 --mu 3.0 --sim-time 200 --animate --out outputs/`
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

- Dependencias fijadas: SimPy, NumPy, Matplotlib, pandas, pytest,
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

**Archivos propios:** `src/mm1/model/simulation.py`, `src/mm1/controller/cli.py`,
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
gráficas) y 5 (animación de la cola y documento).

**Rama y PR:** `feat/jaime-simulation-cli` → PR a `main`.

---

## 6. Bloque 3 — Modelo teórico, escenarios y análisis (Richard Chamba)

**Archivos propios:** `src/mm1/model/metrics.py`, `src/mm1/model/scenarios.py`,
`src/mm1/model/analysis.py`, `tests/test_metrics.py`, `tests/test_scenarios.py`,
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

### Estado de la primera entrega de Richard Chamba — 15/10/2026

| Etapa | Estado | Evidencia |
|-------|--------|-----------|
| Modelo · teoría (fila 2 de `CONTRIBUTING.md`, tareas 2.1–2.4) | ✅ Listo | 17 pruebas de teoría pasan; suite completa: 48 pruebas; ruff sin hallazgos |
| Escenarios, análisis y servicio de estudio (filas 5–7) | ⬜ Pendiente | Corresponden a las siguientes entregas |

Se implementaron `utilization`, `is_stable` y `theoretical_metrics` con las firmas
congeladas, `ρ = λ/μ` (D1) y `ValueError("El sistema no es estable")` para `λ >= μ`.
La comparación de estabilidad es estricta; la tolerancia `1e-9` se usa solo al
comparar resultados numéricos. `TheoryMetrics` conserva su inmutabilidad.

Evidencia ejecutada desde la raíz del repositorio con `.venv/bin/python`:

- RED: `.venv/bin/python -m pytest tests/test_metrics.py -q --tb=line` →
  13 pruebas fallaron con `NotImplementedError` antes de implementar.
- GREEN y PRESERVE: `.venv/bin/python -m pytest tests/test_metrics.py -q -o addopts=''`
  → `17 passed`.
- Suite tras REFACTOR: `.venv/bin/python -m pytest -q -o addopts=''` → `48 passed`.
- Estilo: `.venv/bin/python -m ruff check src tests app` → `All checks passed!`.

La evidencia cubre los tres escenarios, las identidades entre métricas, los casos
`λ = μ` y `λ > μ`, la comparación estricta cerca del límite y la inmutabilidad.
Esta entrega verifica teoría; la simulación y la CLI siguen pendientes.

**Prerrequisitos:** bloque 1 para `metrics.py`; bloque 2 para `scenarios.py` y
`analysis.py` (necesitan `run_mm1`). **Lo consumen:** bloques 4 y 5.

**Rama y PR:** `feat/richard-theory-analysis` → PR a `main` (dos PR si se separa
la parte teórica de la parte de escenarios y análisis).

---

## 7. Bloque 4 — Tabla comparativa y gráficas (Cael Soto)

**Archivos propios:** `src/mm1/view/tables.py`, `src/mm1/view/charts.py`,
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

## 8. Bloque 5 — Animación de la cola y documento (Domenica Rojas)

**Archivos propios:** `src/mm1/view/animation.py`, `tests/test_animation.py`, `reports/ape3_mm1.tex`, `reports/ape3_mm1.pdf`, `reports/README.md`, `reports/assets/**`.
**Specs:** S8 (10 preguntas de control), S9 (criterios de evaluación),
S19 (sin interfaz interactiva; animación headless), S20 (esta re-planificación).

> **La práctica NO tiene interfaz interactiva.** Lo pidió el docente. Se canceló el
> recurso Streamlit: no hay `app/`, no hay página web, no hay deslizadores. Todo se
> hace desde la línea de comandos, que es lo que la guía §5 pide (Python + SimPy +
> NumPy + Matplotlib). Lo único que sobrevive de la etapa anterior es la **animación
> de la cola**, que se renderiza sin pantalla y se dispara con `--animate`.

**Interfaz que debe cumplir** (vive en `src/mm1/view/animation.py`)

```python
def render_queue_animation(run: ScenarioRun, out_dir: str | Path,
                           fps: int = 20, max_frames: int = 200) -> list[Path]
def frame_frames(trace: Sequence[tuple[float, int]], sim_time: float,
                 max_frames: int) -> list[list[tuple[float, int]]]
def queue_animation_figure(run: ScenarioRun, frames: int) -> tuple[Figure, Callable[[int], tuple]]
```

**Regla de capa:** la vista **no calcula** resultados del dominio. El `ScenarioRun`
llega ya corrido desde el motor; la animación solo lo dibuja. El flag `--animate`
lo agrega **Jaime** en `controller/cli.py`: vos no tocás ese archivo.

**Entregables — animación de la cola**

- `render_queue_animation` escribe `cola.mp4` (writer `ffmpeg`) **y** `cola.gif`
  (writer `pillow`) en `out_dir`, y devuelve los dos paths.
- Forzar `matplotlib.use("Agg")` **antes** de importar pyplot, para que no necesite
  pantalla. Verificado: funciona sin display con ffmpeg instalado.
- `frame_frames` muestrea la traza: como máximo `max_frames` sub-trazas, cada una
  arrancando en la primera entrada, la última cubriendo la traza entera.
- Los helpers puros se testean **sin ejecutar el encoder**, así la suite no depende
  de que ffmpeg esté presente.
- Cerrar la figura después de guardar; sin fechas ni marcas de tiempo, para que la
  misma entrada rinda la misma animación.
- Ejes, título y leyenda en español (van al informe). Identificadores y comentarios
  del código en inglés.

**Entregables — documento técnico (`reports/`)**

- Estructura y presentación: título, datos de la práctica y los 4 integrantes,
  objetivos, modelo matemático con la nota de la decisión D1, procedimiento y
  escenarios.
- Procedimiento y resultados con evidencias: la tabla comparativa, el intervalo de
  confianza, el error relativo, las figuras, la animación y el comando
  `python -m mm1 --scenarios --replications 30 --sim-time 1000 --out outputs/` que las
  reproduce. **Usá los números medidos de `docs/resultados_escenarios.md`** en vez de
  recalcularlos: ese archivo es la fuente de verdad y trae la tabla lista para pegar.
- Respuestas a las **10 preguntas de control** de la guía §7, cada una con la
  evidencia simulada que la respalda. Las 10 son estas (textuales de la guía):

  1. ¿Qué representa el modelo M/M/1?
  2. ¿Qué representan λ y μ?
  3. ¿Por qué debe cumplirse λ < μ para que el sistema sea estable?
  4. ¿Qué significa la utilización ρ?
  5. ¿Cuál es la diferencia entre W y Wq?
  6. ¿Cuál es la diferencia entre L y Lq?
  7. ¿Por qué SimPy utiliza una distribución exponencial para generar los tiempos?
  8. ¿Qué sucede con la cola cuando λ se aproxima a μ?
  9. ¿Por qué los resultados simulados pueden ser diferentes de los resultados teóricos?
     (la respuesta medida está en `docs/resultados_escenarios.md` §4b: a ρ = 0.967
     una corrida suelta se desvía hasta 74 % y aun así el simulador es correcto;
     es cola pesada, y la media de 30 réplicas mete la teoría dentro del IC 95 %)
  10. ¿Qué ocurriría si λ fuera mayor que μ?  (la guía lo imprime con `??`; se
      responde una sola vez)

- Conclusiones relacionadas con los tres objetivos de la práctica y con el
  comportamiento esperado de la guía §6 (el tiempo de espera y la cola crecen
  cuando λ se acerca a μ).
- Enlace al **video de demostración** y notas para la defensa oral.

**Criterios de aceptación**

- `python -m pytest tests/test_animation.py -q` pasa.
- `python -m mm1 --lam 2.0 --mu 3.0 --sim-time 200 --animate --out outputs/` sale 0 y
  deja `cola.mp4` y `cola.gif` no vacíos (el flag lo agrega Jaime).
- Ningún archivo del proyecto menciona un framework web ni hay directorio `app/`.
- Las 10 preguntas están numeradas y respondidas; tres de ellas citadas
  textualmente desde la guía.
- Cada figura citada por el documento existe en `reports/figures/`.

**Prerrequisitos:** el motor (bloque 2) para tener un `ScenarioRun` real, y las
figuras del bloque 4. Las etapas 8 y 9 no la bloquean: puede ir en paralelo.

**Rama y PR:** `domenica-rojas` (persistente, no se borra) → PR a `main`.

---

## 9. Orden de integración

Mismo orden que la tabla de [`../CONTRIBUTING.md`](../CONTRIBUTING.md), acá visto por
rama. Es el orden de **integración**; la programación puede adelantarse en paralelo
porque los archivos son disjuntos.

| Orden | Etapa | Rama | Depende de | Resultado verificable |
|-------|-------|------|-----------|------------------------|
| 1 | Fundación (estructura MVC) | `feat/orchestrator-foundation` | — | `python -c "import mm1"` y `python -m pytest -q` verde |
| 2 | Modelo · teoría | `feat/richard-theory-analysis` | 1 | `python -m pytest tests/test_metrics.py -q` |
| 3 | Modelo · motor SimPy | `feat/jaime-simulation-cli` | 1 | `python -m pytest tests/test_simulation.py -q` |
| 4 | Controlador · CLI | `feat/jaime-simulation-cli` | 3 | `python -m mm1 --replications 5 --sim-time 300 --out outputs/` |
| 5 | Modelo · escenarios | `feat/richard-theory-analysis` | 3 | `python -m pytest tests/test_scenarios.py -q` |
| 6 | Modelo · análisis (IC 95 %, error relativo) | `feat/richard-theory-analysis` | 5 | `python -m pytest tests/test_analysis.py -q` |
| 7 | Controlador · servicio `run_study` | `feat/richard-theory-analysis` | 6 | `python -m pytest tests/test_study.py -q` |
| 8 | Vista · tabla comparativa | `feat/cael-tables-charts` | 7 | `python -m pytest tests/test_tables.py -q` |
| 9 | Vista · gráficas | `feat/cael-tables-charts` | 7 | `python -m pytest tests/test_charts.py -q` |
| 10 | **Vista · animación de la cola** (último entregable de código) | `domenica-rojas` | 3 | `python -m pytest tests/test_animation.py -q` y `python -m mm1 --lam 2.0 --mu 3.0 --sim-time 200 --animate --out outputs/` |

Las etapas 2 y 3 pueden hacerse en paralelo, igual que 4 con 5 y 8 con 9. Todos los PR
apuntan a `main` y ninguno debe superar las 400 líneas escritas; si un bloque las
supera, se divide en dos PR del mismo integrante.

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
Tarea: ejecuta las tareas 1.1 a 1.6 de
openspec/changes/ape3-mm1-queue-simulation/tasks.md.
Archivos permitidos: requirements.txt, pyproject.toml, .gitignore, README.md,
CONTRIBUTING.md, src/mm1/__init__.py, src/mm1/__main__.py, src/mm1/model/__init__.py,
src/mm1/view/__init__.py, src/mm1/controller/__init__.py.
Interfaz: copia exactamente la interfaz pública de design.md.
No toques los módulos de src/mm1/model/, src/mm1/view/ ni src/mm1/controller/,
ni app/ ni tests/.
Evidencia obligatoria: salida de "python -m pip install -r requirements.txt",
"python -c \"import mm1\"", "python -m ruff check src" y "git status --short".
```

**Bloque 2 — simulación y CLI (Jaime)**

```text
Tarea: ejecuta las tareas del bloque 2 (3.1 a 3.6) de tasks.md.
Archivos permitidos: src/mm1/model/simulation.py, src/mm1/controller/cli.py,
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
Tarea: ejecuta las tareas del bloque 3 (2.1 a 2.4, 4.1 a 4.7) de tasks.md.
Archivos permitidos: src/mm1/model/metrics.py, src/mm1/model/scenarios.py,
src/mm1/model/analysis.py, src/mm1/controller/study.py, tests/test_metrics.py,
tests/test_scenarios.py, tests/test_analysis.py, tests/test_study.py.
Interfaz: firmas exactas de design.md.
Usa rho = lam / mu (decisión D1); no uses la fórmula impresa en la guía §5.1.
No toques src/mm1/model/simulation.py, src/mm1/controller/cli.py, src/mm1/view/,
app/ ni reports/.
Evidencia obligatoria: salida de
"python -m pytest tests/test_metrics.py tests/test_scenarios.py tests/test_analysis.py tests/test_study.py -q"
con los valores analíticos L, Lq, W y Wq de los tres escenarios.
```

**Bloque 4 — tablas y gráficas (Cael)**

```text
Tarea: ejecuta las tareas del bloque 4 (5.1 a 5.5) de tasks.md.
Archivos permitidos: src/mm1/view/tables.py, src/mm1/view/charts.py,
tests/test_tables.py, tests/test_charts.py, reports/figures/.
Interfaz: firmas exactas de design.md; usa matplotlib con backend Agg.
No toques src/mm1/model/ ni src/mm1/controller/, ni src/mm1/view/tables.py,
ni src/mm1/view/charts.py.
Evidencia obligatoria: salida de
"python -m pytest tests/test_tables.py tests/test_charts.py -q" y el listado
de archivos generados por "python -m mm1 --replications 5 --sim-time 300 --out outputs/".
```

**Bloque 5 — animación de la cola y documento (Domenica)**

```text
Tarea: ejecuta las tareas del bloque 5 (6.1 a 6.8) de tasks.md.
Archivos permitidos: src/mm1/view/animation.py, tests/test_animation.py,
reports/ape3_mm1.tex, reports/ape3_mm1.pdf, reports/README.md, reports/assets/**.
Interfaz: render_queue_animation, frame_frames y queue_animation_figure con las
firmas exactas de design.md.
La practica NO tiene interfaz interactiva: no hay app/, no hay pagina web, no hay
deslizadores. La animacion es un archivo (mp4 y gif) que se genera sin pantalla con
matplotlib.animation. Nada de streamlit.
La vista no calcula: recibe un ScenarioRun ya corrido por el motor y solo lo dibuja.
Forza matplotlib.use("Agg") ANTES de importar pyplot, y cierra la figura al guardar.
Los helpers puros (frame_frames, queue_animation_figure) se testean sin ejecutar el
encoder, para que la suite no dependa de ffmpeg.
El flag --animate del CLI lo agrega Jaime en src/mm1/controller/cli.py: no toques ese archivo.
El documento usa los numeros medidos de docs/resultados_escenarios.md, responde las 10
preguntas de control de la guia §7 e incluye el enlace al video de demostracion.
No toques src/mm1/model/, src/mm1/controller/, ni src/mm1/view/tables.py y
src/mm1/view/charts.py; de tests/ solo tests/test_animation.py.
Evidencia obligatoria: salida de "python -m pytest tests/test_animation.py -q",
la lista de secciones y figuras del documento, y confirmacion de que ningun archivo
menciona un framework web.
```

### 10.3 Evidencia obligatoria en cada entrega del agente

| Elemento | Ejemplo |
|----------|---------|
| Archivos modificados | `git status --short` con solo archivos del bloque |
| Prueba RED | Comando ejecutado y su salida fallida |
| Prueba GREEN | `python -m pytest tests/test_<modulo>.py -q` con el resumen final |
| Estilo | `python -m ruff check src tests app` sin hallazgos |
| Demostración | Salida de `python -m mm1 --scenarios --out outputs/` y de `--animate` |
| Riesgos | Qué quedó pendiente y qué no se pudo verificar |

---

## 11. Criterios de evaluación y responsables

| Criterio de la guía §8 | Peso | Responsables |
|------------------------|------|--------------|
| Defensa oral y demostración | 4/10 | Todos; Jaime explica el motor y la CLI, Richard el modelo matemático, Cael las gráficas, Domenica la animación de la cola y el documento |
| Implementación | 3/10 | Jaime (motor y CLI), Richard (teoría, escenarios, análisis), Cael (tablas y gráficas) |
| Documento | 3/10 | Domenica (estructura, resultados, 10 preguntas, conclusiones, video), con evidencias de Cael |

**Video de demostración:** lo graba Domenica con la participación de cada
integrante en su bloque, mostrando `python -m mm1 --out outputs/` y el recurso
interactivo.
