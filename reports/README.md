# reports/

Esta carpeta reúne los entregables **redactados** de la APE 003.

## Documento técnico

| Archivo | Qué es |
|---|---|
| `ape3_mm1.tex` | Fuente LaTeX del informe |
| `ape3_mm1.pdf` | PDF compilado (9 páginas) |
| `referencias.bib` | Bibliografía |
| `assets/logo_feirnnr.png` | Logo institucional del encabezado |
| `figures/` | Figuras insertadas en el informe |
| `assets/notas_defensa.md` | Guion y notas para la defensa oral (etapa 10) |
| `assets/animacion_cola_frames.png` | Fotogramas de la animación de la cola (evidencia) |

El documento sigue el formato de
[`docs/guia/PLANTILLA_APE_LATEX/reporte_tecnico_overleaf.tex`](../docs/guia/PLANTILLA_APE_LATEX/reporte_tecnico_overleaf.tex)
y cubre los tres criterios que califica la guía §8: estructura y presentación,
procedimiento y evidencias, y conclusiones atadas a los objetivos.

Los números del informe salen de `docs/resultados_escenarios.md`, que es el registro
de la corrida oficial. **No se copian a mano**: se regeneran con

```bash
python -m mm1 --scenarios --replications 30 --sim-time 1000 --out outputs/
```

y luego se actualiza el registro y las tablas del informe con esos valores.

### Cómo compilar

Con Overleaf: subir `ape3_mm1.tex`, `referencias.bib`, `assets/` y `figures/`,
y compilar con pdfLaTeX o XeLaTeX.

Localmente, con Tectonic:

```bash
tectonic --bundle ~/.cache/tectonic-bundles/tlextras-2022.0r0 \
         --only-cached -o . ape3_mm1.tex
```

> **Nota sobre los caracteres.** El documento compila con XeTeX, que ignora
> `inputenc`. Con `T1` + Helvetica, escribir `¿` literal produce el glifo equivocado
> (`£`). Por eso el fuente usa `\textquestiondown{}` en lugar del carácter literal:
> es el comando que garantiza el signo correcto. **No reemplaces esos comandos por
> el carácter `¿` al editar**, y aplicá lo mismo a `¡`, `«` y `»`.

## Animación de la cola (etapa 10)

La práctica **no tiene interfaz interactiva** (lo pidió el docente), así que el recurso
gráfico es la animación de la cola, que se genera como archivo y sin pantalla
(`matplotlib.animation` con backend `Agg`) desde la línea de comandos:

```bash
python -m mm1 --lam 2.0 --mu 3.0 --sim-time 200 --animate --out outputs/
```

Escribe `outputs/cola.mp4` (writer FFmpeg) y `outputs/cola.gif` (writer Pillow). La
misma entrada rinde la misma animación: no se dibuja ninguna fecha ni marca de tiempo.

Corrida de referencia de esta etapa (`lam = 2.0`, `mu = 3.0`, `sim_time = 200`,
`seed = 42`, 200 fotogramas a 20 fps, traza de 793 entradas):

| Archivo | Tamaño |
|---|---|
| `outputs/cola.mp4` | 65 248 bytes |
| `outputs/cola.gif` | 1 079 201 bytes |

El MP4 necesita `ffmpeg` en el `PATH`; el GIF sólo necesita Pillow. **La suite de
pruebas no depende de `ffmpeg`**: las funciones puras (`frame_frames`,
`queue_animation_figure`) se prueban sin ejecutar el codificador y la prueba del
codificador se salta cuando `ffmpeg` no está instalado.

`assets/animacion_cola_frames.png` es un fotograma doble (mitad y final de la corrida)
sacado de ese GIF, y `assets/notas_defensa.md` tiene el guion de la defensa, con el
recorrido del código y las preguntas esperadas.

## Pendientes

- [ ] **Enlace al video de demostración.** El video debe mostrar la ejecución desde la
      línea de comandos: la corrida de los tres escenarios, la generación de la tabla
      comparativa y de las figuras, y la animación de la cola. El documento tiene una
      marca visible `PENDIENTE` en la sección *Demostración* donde va el enlace. Los
      comandos que se graban y el reparto por integrante están en
      `assets/notas_defensa.md`.
- [x] **Animación de la cola** (`cola.mp4` / `cola.gif` en `outputs/`), el último
      entregable de código (etapa 10, `view/animation.py`) — ver la sección anterior.
      El informe todavía tiene su marca `\pendiente{}` para la animación, así que
      queda pendiente **citarla** en el documento e insertar los fotogramas.

## Regla de artefactos

Los artefactos **generados** por el código (CSV, tablas LaTeX, PNG, `cola.mp4` y
`cola.gif`) van en `outputs/`, no aquí. Esa carpeta se ignora en git y su contenido
siempre debe poder regenerarse ejecutando la CLI. Lo que sí se versiona en `reports/`
es el documento redactado, su bibliografía, las notas de defensa y **las figuras
definitivas** que cita el informe.
