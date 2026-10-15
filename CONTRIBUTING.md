# Contribuir — APE 003: Simulación M/M/1 con SimPy

Guía de trabajo del equipo. Acá está **en qué orden se hacen los aportes, quién es
responsable de cada uno y cómo se comprueba**, desde la base hasta el recurso visual
interactivo, que es el entregable final del código.

- Integrantes: **Jaime Landazuri**, **Richard Chamba**, **Cael Soto**, **Domenica Rojas**.
- Asignatura: Simulación (5.º ciclo, FEIRNNR — Carrera de Computación). Práctica 003.
- Guía oficial: [`docs/guia/ape3_guia_simulacion_semana3.pdf`](docs/guia/ape3_guia_simulacion_semana3.pdf)
  (texto legible por agentes: [`docs/guia/ape3_guia_simulacion_semana3.txt`](docs/guia/ape3_guia_simulacion_semana3.txt)).
- Plan técnico completo: [`openspec/changes/ape3-mm1-queue-simulation/`](openspec/changes/ape3-mm1-queue-simulation/).
- Detalle por integrante (archivos, prompts, evidencia): [`docs/division-trabajo.md`](docs/division-trabajo.md).

---

## 1. Orden de aportes — de la base al recurso visual

El orden manda: cada etapa usa lo que dejó la anterior. En la columna *Paralelo* se
indica qué se puede hacer al mismo tiempo sin pisarse.

| # | Etapa | Aporte | Responsable | Depende de | Paralelo con | Rama | Cómo se comprueba | Estado |
|---|-------|--------|-------------|------------|--------------|------|-------------------|--------|
| 1 | Fundación | Estructura MVC (`model/`, `view/`, `controller/`), packaging, facades de las 3 capas, `README.md`, `CONTRIBUTING.md` | Jaime Landazuri | — | — | `feat/orchestrator-foundation` | `pytest -q` verde · `python -m mm1 --help` resuelve · `import mm1` no importa streamlit | ✅ Hecho |
| 2 | Modelo · teoría | `model/metrics.py`: `ρ = λ/μ`, `L`, `Lq`, `W`, `Wq` y la guarda de estabilidad | Richard Chamba | 1 | con 3 | `feat/richard-theory-analysis` | `pytest tests/test_metrics.py -q` | ⬜ Pendiente |
| 3 | Modelo · motor | `model/simulation.py`: SimPy, un servidor, FIFO, registro de clientes y traza de cola | Jaime Landazuri | 1 | con 2 | `feat/jaime-simulation-cli` | `pytest tests/test_simulation.py -q` | ⬜ Pendiente |
| 4 | Controlador · CLI | `controller/cli.py`: `python -m mm1` corre los 3 escenarios y exporta | Jaime Landazuri | 3 | con 5 | `feat/jaime-simulation-cli` | `python -m mm1 --replications 5 --sim-time 300 --out outputs/` → salida 0 | ⬜ Pendiente |
| 5 | Modelo · escenarios | `model/scenarios.py`: los 3 escenarios de la guía y las réplicas con semillas | Richard Chamba | 3 | con 4 | `feat/richard-theory-analysis` | `pytest tests/test_scenarios.py -q` | ⬜ Pendiente |
| 6 | Modelo · análisis | `model/analysis.py`: agregación, IC 95 % y error relativo teórico vs simulado | Richard Chamba | 5 | — | `feat/richard-theory-analysis` | `pytest tests/test_analysis.py -q` | ⬜ Pendiente |
| 7 | Controlador · servicio | `controller/study.py`: `run_study`, **el servicio que comparten la CLI y la app** | Richard Chamba | 6 | — | `feat/richard-theory-analysis` | `pytest tests/test_study.py -q` | ⬜ Pendiente |
| 8 | Vista · tabla | `view/tables.py`: tabla comparativa de 19 columnas, CSV y LaTeX | Cael Soto | 7 | con 9 | `feat/cael-tables-charts` | `pytest tests/test_tables.py -q` | ⬜ Pendiente |
| 9 | Vista · gráficas | `view/charts.py`: evolución de la cola, tiempos de espera, teoría vs simulación, comparación de escenarios | Cael Soto | 7 | con 8 | `feat/cael-tables-charts` | `pytest tests/test_charts.py -q` | ⬜ Pendiente |
| 10 | **Vista · recurso interactivo** | `view/streamlit_view.py` + `app/streamlit_app.py`: sliders de λ y μ, aviso de estabilidad, animación de la cola, tabla viva y gráficas interactivas | Domenica Rojas | 7, 8, 9 | — | `feat/domenica-streamlit-document` | `pytest tests/test_app.py -q` y `streamlit run app/streamlit_app.py` arranca | ⬜ Pendiente |

> **La fila 10 es el entregable final del código: el recurso visual.**
> Nada después de la fila 10 modifica el programa; lo que sigue es el cierre de la
> práctica (documento, video y defensa) descrito en la sección 2.

### Por qué este orden y no otro

- **2 y 3 son independientes**: la teoría es matemática pura y el motor es SimPy. Los
  dos se pueden escribir a la vez porque la interfaz ya está congelada en `design.md`.
- **4 y 5 pueden ir juntos**: la CLI ya corre el motor, y los escenarios son datos.
- **6 necesita 5** porque agregar réplicas requiere que existan las corridas.
- **7 es la bisagra**: hasta acá hay piezas sueltas; con `run_study` existe *una* forma
  de obtener todos los resultados. Por eso la app y el documento no pueden divergir.
- **8 y 9 son independientes entre sí** y ambos consumen `ScenarioSummary`.
- **10 va último** porque muestra todo lo anterior junto y en vivo.

---

## 2. Cierre de la práctica (posterior al recurso visual)

Estos entregables son de la guía (§6, §8) y se hacen **después** de la fila 10:

| # | Etapa | Aporte | Responsable | Depende de | Cómo se comprueba |
|---|-------|--------|-------------|------------|-------------------|
| 11 | Documento técnico | Estructura, procedimiento, tabla comparativa, figuras, **las 10 preguntas de control**, conclusiones atadas a los objetivos | Domenica Rojas | 8, 9, 10 | PDF en `reports/`; cada figura citada existe en `reports/figures/` y sale de `python -m mm1 --out outputs/` |
| 12 | Video de demostración | Grabación corta del recurso funcionando en los 3 escenarios | Domenica Rojas | 10 | Enlace en `reports/README.md` |
| 13 | Defensa oral | Dominio del modelo, recorrido del código y demo en vivo | Los 4 | 10, 11 | Preguntas de control de la guía §7 respondidas por cualquier integrante |

---

## 3. Cómo se trabaja

### Ramas y PRs

- Una rama por etapa, con el nombre de la tabla: `feat/<nombre>-<tema>`.
- Un PR por etapa, contra `main`. Un PR = una etapa, no varias.
- Nadie edita archivos que no le pertenecen (la tabla de propiedad está en
  `openspec/changes/ape3-mm1-queue-simulation/tasks.md` y en
  `docs/division-trabajo.md`). Si necesitás tocar un archivo ajeno, avisá en el PR
  antes de hacerlo.
- Mantené el PR y su revisión **por debajo de ~400 líneas cambiadas**. Si se pasa,
  partilo en dos: el recurso se agradece, la gente se cansa de revisar.

### Commits

Formato [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`,
`test:`, `docs:`, `refactor:`, `chore:`. Sin atribución a IA.

Ejemplos:

```text
feat(model): implement the M/M/1 theoretical metrics
test(model): add RED tests for the SimPy engine
docs(reports): answer the ten control questions
```

### Antes de pedir revisión (Definition of Done de una etapa)

1. El test en rojo existía y ahora pasa: `python -m pytest tests/<tu_test>.py -q`.
2. La suite completa sigue verde: `python -m pytest -q`.
3. El linter está limpio: `python -m ruff check src tests app`.
4. Escribiste el código **y** su test **y** la documentación que tu cambio invalida,
   en el mismo PR.
5. Pegaste en el PR el comando exacto que corriste y su salida.

### Regla de trabajo adelantado

Nadie abre un PR de una etapa cuyas dependencias no están en `main`. Se puede
*escribir* en paralelo apoyándose en las interfaces congeladas, pero se *integra* en
orden.

---

## 4. Reglas de las capas (MVC)

El proyecto está en tres capas y la dirección de dependencias es obligatoria:

| Capa | Carpeta | Contiene | Regla |
|------|---------|----------|-------|
| Modelo | `src/mm1/model/` | Teoría, motor SimPy, escenarios, estadística | **No** renderiza ni escribe archivos. **Nunca** importa `mm1.view` ni `mm1.controller`. |
| Vista | `src/mm1/view/` | Figuras, tabla comparativa, página de Streamlit | Solo presenta. **No** calcula resultados del dominio: se los pide a `mm1.controller`. |
| Controlador | `src/mm1/controller/` | `run_study` y la CLI | Es la única capa que conoce a las otras dos. |

`app/streamlit_app.py` es un punto de entrada fino: solo llama a
`view.streamlit_view.render()`. Así el comando documentado sigue siendo corto.

---

## 5. Trabajar con agentes de IA

Cada integrante trabaja con su agente sobre **sus** archivos. Prompt sugerido
(completá lo que está entre `<>`):

```text
Tarea: implementa la etapa <N> de CONTRIBUTING.md para la práctica APE 003.
Contexto obligatorio, en este orden:
  1. docs/guia/ape3_guia_simulacion_semana3.txt  (la guía oficial)
  2. openspec/changes/ape3-mm1-queue-simulation/design.md   (interfaces congeladas)
  3. openspec/changes/ape3-mm1-queue-simulation/tasks.md    (tu etapa, tareas N.x)
  4. CONTRIBUTING.md (esta tabla) y docs/division-trabajo.md
Archivos que podés tocar, y solo estos:
  <tus archivos según la tabla>
Interfaz que debés respetar: las firmas de design.md, tal cual.
Trabajá con test-first: escribí primero el test en rojo, mostrame que falla,
y recién después el código.
Evidencia que tenés que devolverme:
  - el comando exacto que corriste y su salida
  - qué quedó cubierto y qué no
  - si tocaste algo fuera de tu lista, decilo explícitamente
No hagas commit ni push: eso lo hago yo.
```

Reglas para el agente:

- **Un archivo, un dueño.** Si el agente dice que necesita tocar un archivo de otra
  etapa, frená y hablalo con el equipo.
- **Test-first.** El test en rojo es la prueba de que entendiste el requisito.
- **Evidencia, no afirmaciones.** Un "ya funciona" sin el comando y su salida no cuenta.
- **La interfaz no se negocia a mitad de camino.** Si creés que la firma de
  `design.md` está mal, se discute en el PR antes de cambiarla, porque los otros tres
  están escribiendo contra ella.

---

## 6. Problemas frecuentes

| Síntoma | Causa y solución |
|---------|------------------|
| `No module named mm1` | Falta el install editable: `python -m pip install -e .` (o `PYTHONPATH=src`). |
| Querés importar `mm1` y te falta Streamlit | Correcto: `import mm1` no debe traer Streamlit. No lo agregues a `view/__init__.py`. |
| `ρ` te da 1,5 con λ = 2,0 y μ = 3,0 | Estás usando `ρ = μ/λ`, que es el typo de la guía §5.1. Va `ρ = λ/μ`. |
| El sistema "no es estable" con λ = 3,0 y μ = 3,0 | Es correcto: la guía exige `λ < μ` y el programa imprime `El sistema no es estable`. |
