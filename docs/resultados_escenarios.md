# Resultados de los tres escenarios — registro de medición

**Qué es este archivo.** El registro de la corrida oficial del proyecto y los números que
el documento debe reportar. **No es el documento de la práctica**: el documento vive en
`reports/` y es de Domenica Rojas. Esto es la fuente de verdad de las mediciones, para que
nadie tenga que re-deducir cifras ni confiar en números copiados a mano.

**Comando que generó todo** (un solo comando, reproducible):

```bash
python -m mm1 --scenarios --replications 30 --sim-time 1000 --out outputs/
```

**Parámetros de la corrida oficial:** 30 réplicas por escenario, `sim_time = 1000`
unidades, `base_seed = 42` (las semillas de cada réplica se derivan de ahí con
`sha256`, así que son estables entre procesos y máquinas). Total: 90 corridas.

**Artefactos en `outputs/`** (184 archivos, `outputs/` está ignorado por git porque se
regenera): `comparacion.csv`, `comparacion.tex` y 182 PNG (60 por escenario más las dos
figuras de resumen).

---

## 1. Tabla comparativa teórico vs. simulado (la que pide la guía §5.1)

| Escenario | λ | μ | ρ | L | Lq | W | Wq | Espera prom. simulada | Cola prom. simulada |
|:---------:|:---:|:---:|:------:|:-------:|:-------:|:------:|:------:|:---------------------:|:-------------------:|
| 1 — Sistema estable | 2.0 | 3.0 | 0.6667 | 2.0000 | 1.3333 | 1.0000 | 0.6667 | **0.6885** | **1.3921** |
| 2 — Mayor utilización | 2.5 | 3.0 | 0.8333 | 5.0000 | 4.1667 | 2.0000 | 1.6667 | **1.6211** | **4.0694** |
| 3 — Cerca de saturación | 2.9 | 3.0 | 0.9667 | 29.0000 | 28.0333 | 10.0000 | 9.6667 | **8.5078** | **24.7945** |

Las columnas `ρ, L, Lq, W, Wq` son **teóricas** (guía §5.1, con `ρ = λ/μ` y no el `μ/λ`
que imprime la guía por error — ver la nota de la sección 4). Las dos últimas columnas son
**simuladas**: la media de las 30 réplicas.

## 2. Intervalo de confianza y error relativo

El intervalo es el de **t de Student al 95 % de la media** de las réplicas (no la
dispersión de clientes individuales). Es la evidencia que sostiene la afirmación del
informe: *la teoría cae dentro del intervalo simulado*.

| Escenario | IC 95 % de la espera simulada | ¿Contiene al teórico? | err. `L` | err. `Lq` | err. `W` | err. `Wq` |
|:---------:|:-----------------------------:|:---------------------:|:--------:|:---------:|:--------:|:---------:|
| 1 | [0.6518, 0.7252] | **sí** (0.6667) | 3.19 % | 4.41 % | 2.23 % | 3.28 % |
| 2 | [1.4755, 1.7666] | **sí** (1.6667) | 2.12 % | 2.33 % | 2.27 % | 2.73 % |
| 3 | [5.4223, 11.5933] | **sí** (9.6667) | 12.69 % | 11.55 % | 11.59 % | 11.99 % |

## 3. Tabla lista para pegar en LaTeX

```latex
\begin{table}[htbp]
  \centering
  \caption{Comparación de resultados teóricos y simulados por escenario}
  \label{tab:comparacion}
  \begin{tabular}{cccccccccc}
    \toprule
    Esc. & $\lambda$ & $\mu$ & $\rho$ & $L$ & $L_q$ & $W$ & $W_q$
         & Espera sim. & Cola sim. \\
    \midrule
    1 & 2.0 & 3.0 & 0.6667 & 2.0000 & 1.3333 & 1.0000 & 0.6667 & 0.6885 & 1.3921 \\
    2 & 2.5 & 3.0 & 0.8333 & 5.0000 & 4.1667 & 2.0000 & 1.6667 & 1.6211 & 4.0694 \\
    3 & 2.9 & 3.0 & 0.9667 & 29.0000 & 28.0333 & 10.0000 & 9.6667 & 8.5078 & 24.7945 \\
    \bottomrule
  \end{tabular}
\end{table}
```

Nota: `outputs/comparacion.tex` genera el mismo flotante con **19 columnas** (agrega
`std_wait`, `ci95_low`, `ci95_high` y los cuatro errores relativos). Para el cuerpo del
documento conviene la versión de arriba, más legible; el `.tex` completo sirve como
respaldo y ya trae el `\label{tab:comparacion}` para citar con `\ref{tab:comparacion}`.

## 4. Notas que el documento necesita

**a) El typo de la guía §5.1.** La guía imprime `ρ = μ/λ`, que contradice su propia
condición de estabilidad `λ < μ`: con esa fórmula los tres escenarios darían
`ρ = 1.5`, `1.2` y `1.03`, o sea un servidor saturado en los tres casos, y `L`, `Lq`, `W` y
`Wq` no existirían. El proyecto implementa `ρ = λ/μ`, que es lo que la propia guía usa en
su pseudocódigo. Está documentado como decisión **D1** en
`openspec/changes/ape3-mm1-queue-simulation/design.md` y conviene explicarlo en la defensa.

**b) Respuesta cuantitativa a la pregunta de control 9** («¿por qué los resultados
simulados pueden ser diferentes de los teóricos?»). El escenario 3 es la respuesta medida:

- Con `ρ = 0.967` el tiempo de espera tiene **cola pesada**: una corrida suelta puede
  desviarse hasta **74 %** de la teoría.
- La media de 30 réplicas baja el error a **12 %**, y la teoría cae **dentro** del
  intervalo de confianza al 95 %.
- El error baja al alargar la corrida (en el escenario 1: 12.9 % con `sim_time = 500`,
  5.7 % con 2000, 2.5 % con 10 000 y 1.6 % con 50 000), así que el simulador es
  **consistente, no sesgado**.
- La ley de Little (`L = λ·W`) se cumple sobre los resultados simulados con menos de
  **0.9 %** de desvío, lo que es una comprobación interna independiente.
- La simulación **no está mal**: es que una sola corrida no es evidencia cuando el sistema
  está cerca de saturarse. Por eso el proyecto promedia réplicas y reporta el intervalo.

**c) El comportamiento que pide la guía §6.** Los resultados lo confirman en las dos
direcciones: a medida que λ se acerca a μ, la utilización crece (0.67 → 0.83 → 0.97) y
**tanto el tiempo de espera como el largo de la cola crecen fuertemente**
(`Wq`: 0.69 → 1.62 → 8.51; `Lq`: 1.39 → 4.07 → 24.79). Eso es exactamente el
comportamiento esperado que la guía pide analizar.

## 5. Cómo regenerar estos números

```bash
python -m pip install -e .                                # una vez
python -m mm1 --scenarios --replications 30 --sim-time 1000 --out outputs/
```

Los números son **idénticos** en cada corrida porque las semillas se derivan de
`base_seed = 42` de forma estable entre procesos. Cambiar `--replications`, `--sim-time`
o `--seed` cambia los resultados, y en ese caso hay que actualizar este archivo: la tabla
del documento y estos números tienen que salir del mismo comando.

## 6. Qué falta de este borrador

Todo lo demás del documento es de `reports/` y de Domenica Rojas: portada y datos de la
práctica, modelo matemático desarrollado, procedimiento, las **10 preguntas de control**
respondidas (la lista textual está en `docs/division-trabajo.md`), conclusiones atadas a
los objetivos, y el **video de demostración**. El recurso interactivo de Streamlit
—etapa 10— también es suyo y puede mostrar exactamente estos números en vivo, porque sale
de `controller.study.run_study`: el mismo camino que produjo esta tabla.
