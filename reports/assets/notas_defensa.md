# Notas para la defensa oral — APE 003 (M/M/1 con SimPy)

Responsable del bloque: **Domenica Rojas**. Estas notas acompañan al documento
(`reports/ape3_mm1.tex`) y citan las decisiones de
`openspec/changes/ape3-mm1-queue-simulation/design.md` por su código (`D1`, `D8`,
`D11`…), porque la defensa pide justificar el diseño, no solo mostrar números.

Reparto sugerido de la exposición (guía §8: defensa oral y demostración = 4/10):

| Integrante | Qué explica |
|---|---|
| Richard Chamba | Modelo matemático, decisión D1, escenarios y análisis estadístico |
| Jaime Landazuri | Motor SimPy, semillas reproducibles y línea de comandos |
| Cael Soto | Tabla comparativa y las cuatro gráficas del informe |
| Domenica Rojas | Animación de la cola, documento, las 10 preguntas y el video |

---

## 1. Recorrido del modelo (2 minutos)

1. **Notación de Kendall**: M/M/1 = llegadas de Poisson, servicio exponencial, un
   servidor, cola infinita, FIFO.
2. **Parámetros**: λ = tasa de llegada, μ = tasa de servicio; `1/λ` y `1/μ` son los
   tiempos medios. En la práctica μ = 3,0 fijo y λ ∈ {2,0; 2,5; 2,9}.
3. **Utilización**: ρ = λ/μ. **Acá está la decisión D1**: la guía §5.1 imprime
   `ρ = μ/λ`, que contradice su propia condición de estabilidad λ < μ (daría ρ > 1 en
   los tres escenarios y ninguna fórmula tendría sentido). El proyecto implementa
   `ρ = λ/μ`, que es lo que la propia guía usa en su pseudocódigo. Conviene decirlo
   antes de que lo pregunten.
4. **Estabilidad**: λ < μ ⇔ ρ < 1. Si λ ≥ μ la cola crece sin límite; el programa
   imprime exactamente `El sistema no es estable` y no escribe archivos.
5. **Fórmulas**: `L = λ/(μ−λ)`, `Lq = λ²/(μ(μ−λ))`, `W = 1/(μ−λ)`,
   `Wq = λ/(μ(μ−λ))`, y las dos identidades que usamos como control:
   `W = Wq + 1/μ` y `L = Lq + ρ`.

## 2. Recorrido del código (3 minutos)

Arquitectura MVC con dirección de dependencias verificable (S16, D13):

```
src/mm1/
├── model/        # NO importa las otras capas
│   ├── metrics.py      # ρ, L, Lq, W, Wq — el oráculo teórico (D1, D2)
│   ├── simulation.py   # motor SimPy: 1 servidor, FIFO, registros inmutables
│   ├── scenarios.py    # los 3 escenarios y las réplicas con semilla derivada (D4)
│   └── analysis.py     # media, IC 95 % con t de Student, error relativo (D15)
├── view/         # solo dibuja; no calcula dominio
│   ├── tables.py       # tabla comparativa → CSV y LaTeX
│   ├── charts.py       # cuatro figuras con backend Agg (D6)
│   └── animation.py    # animación headless de la cola (D16, D17)
└── controller/
    ├── study.py        # run_study: el servicio que comparten CLI, tabla y figuras (D14)
    └── cli.py          # python -m mm1 — único punto de entrada (D8, D11)
```

Puntos que hay que saber defender:

- **`__main__.py` (D11)**: es un shim de tres líneas para que `python -m mm1`
  funcione; la lógica de despacho sigue en `cli.main`.
- **Semillas (D4)**: no hay una semilla global. La de cada réplica sale de
  `sha256("42:escenario:réplica")`, así que 90 corridas son idénticas en cualquier
  máquina y el orden de los escenarios no altera nada.
- **`run_study` (D14)**: el documento no puede contradecir a los artefactos porque
  tabla, figuras y animación salen del mismo servicio.
- **IC 95 % (D15)**: es el intervalo de Student de la **media de las réplicas**, con
  `mean ± t(0.975, n−1)·s/√n`, implementado con biblioteca estándar (sin SciPy).
- **Animación (D16, D17)**: la práctica **no tiene interfaz interactiva** (lo pidió el
  docente): se descartó el recurso de interfaz gráfica previsto. El recurso gráfico es la
  animación, que se genera como archivo con `matplotlib.animation` y backend `Agg`, sin
  pantalla, y se dispara con `--animate` desde la CLI.
- **Backend `Agg`**: se fuerza **antes** de importar pyplot, entre los imports del
  módulo; por eso la suite y la generación corren en un servidor sin display.

## 3. Demostración en vivo (3 minutos)

```bash
python -m pip install -r requirements.txt                    # una vez
python -m mm1 --scenarios --replications 30 --sim-time 1000 --out outputs/
python -m mm1 --lam 2.0 --mu 3.0 --sim-time 200 --animate --out outputs/
python -m pytest -q
```

Qué mirar en cada paso:

1. Primero muestra la tabla comparativa y los PNG en `outputs/`.
2. Después `cola.mp4` y `cola.gif`: la cola crece como escalón y el caption muestra
   el tiempo simulado.
3. Un caso inestable para cerrar: `python -m mm1 --lam 3.0 --mu 3.0` imprime
   `El sistema no es estable` y no escribe nada.

## 4. Preguntas que la guía §7 hace y cómo se responden

Las diez están desarrolladas en la §5 del documento. Resumen de una línea cada una:

1. **M/M/1** — Poisson + exponencial + un servidor + FIFO + cola infinita.
2. **λ y μ** — tasas de llegada y de servicio por unidad de tiempo.
3. **λ < μ** — la capacidad de servicio debe superar la carga; si no, la cola diverge.
4. **ρ** — fracción del tiempo con el servidor ocupado (0,6667 / 0,8333 / 0,9667).
5. **W vs Wq** — W incluye el servicio: `W = Wq + 1/μ` (verificado: 0,3333 en los tres).
6. **L vs Lq** — L incluye al cliente en servicio: `L = Lq + ρ` (verificado 3/3).
7. **Exponencial** — es la única distribución sin memoria ⇒ llegadas de Poisson ⇒
   fórmulas cerradas válidas.
8. **λ → μ** — la cola y la espera crecen muy rápido (`Lq` simulado 1,39 → 4,07 → 24,79).
9. **Simulado ≠ teórico** — cola pesada: a ρ = 0,967 una corrida suelta se desvía 74 %
   y aun así es correcta; la media de 30 réplicas baja a 12 % y mete la teoría dentro
   del IC 95 %; el error baja al alargar la corrida (1,6 % con `sim_time = 50 000`).
10. **λ > μ** — sistema inestable: la cola crece sin límite y las fórmulas no aplican;
    el programa rechaza el caso explícitamente.

Preguntas adicionales que conviene tener preparadas:

- *¿Por qué 30 réplicas y no 10?* Por la pregunta 9: cerca de la saturación la varianza
  es enorme; 30 réplicas dan un intervalo lo bastante angosto para que la teoría caiga
  dentro en los tres escenarios.
- *¿Por qué el error del escenario 3 es el mayor (hasta 12,7 %)?* Por la cola pesada de
  `Wq` cuando ρ → 1; no es sesgo: el error baja al alargar el horizonte.
- *¿Por qué no hay app web ni interfaz interactiva?* Lo pidió el docente (S19); la
  demostración es la terminal, que es lo que la guía §5 siempre pidió.
- *¿La animación calcula algo?* No: recibe un `ScenarioRun` ya corrido por el motor y
  solo lo dibuja (regla de capa de la vista).

## 5. Riesgos y limitaciones que conviene declarar

- El escenario 3 es el más frágil: su IC 95 % de la espera es ancho (`[5,42; 11,59]`)
  justamente porque la distribución tiene cola pesada.
- Las figuras por escenario muestran la **primera réplica** (`escenario_N_replica_1_*`),
  no el promedio: son ilustrativas del comportamiento, y los números que se citan en el
  informe son los de la tabla comparativa.
- La animación necesita `ffmpeg` en el `PATH` para el MP4; el GIF solo necesita Pillow.
  La suite no depende de `ffmpeg`: la prueba del codificador se saltea si no está.
