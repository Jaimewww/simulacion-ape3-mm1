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

## Pendientes

- [ ] **Enlace al video de demostración.** El video debe mostrar la ejecución desde la
      línea de comandos: la corrida de los tres escenarios, la generación de la tabla
      comparativa y de las figuras, y la animación de la cola. El documento tiene una
      marca visible `PENDIENTE` en la sección *Demostración* donde va el enlace.
- [ ] **Animación de la cola** (`cola.mp4` / `cola.gif` en `outputs/`), que es el
      último entregable de código (etapa 10, `view/animation.py`).

## Regla de artefactos

Los artefactos **generados** por el código (CSV, tablas LaTeX, PNG y video) van en
`outputs/`, no aquí. Esa carpeta se ignora en git y su contenido siempre debe poder
regenerarse ejecutando la CLI. Lo que sí se versiona en `reports/` es el documento
redactado, su bibliografía y **las figuras definitivas** que cita el informe.
