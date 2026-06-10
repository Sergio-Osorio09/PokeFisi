# Informe PokeFisi (formato ACL)

Informe en LaTeX siguiendo la plantilla oficial de la *Association for
Computational Linguistics* (ACL).

## Archivos
- `main.tex` — documento principal (español, formato ACL).
- `custom.bib` — bibliografía.
- `figs/` — figuras generadas por los experimentos (una por experimento, PDF + PNG).
- `results/` — resultados numéricos de cada experimento (JSON).
- `run_experiments.py` — los cinco experimentos del informe (genera resultados y figuras).
- `run_log.txt` — log de la última ejecución.

## Los cinco experimentos
- **A — Torneo todos contra todos** (7 agentes): jerarquía de los agentes.
- **B — Poda alfa-beta**: coste de búsqueda con y sin poda (y coste de evaluar 4 vs 6 componentes).
- **C — Profundidad y calidad**: ¿mirar más turnos mejora el win-rate?
- **D — Sobreajuste del genético**: ¿diversificar el entrenamiento (panel de rivales) ayuda a generalizar?
- **E — Techo de la evaluación**: cuatro vs seis componentes; el límite estructural del dominio.

## Cómo compilar (Overleaf, recomendado)
1. Abre la plantilla ACL: <https://www.overleaf.com/latex/templates/association-for-computational-linguistics-acl-conference/jvxskxpnznfj>.
2. Reemplaza el `main.tex` de la plantilla por este `main.tex`.
3. Sube `custom.bib` y la carpeta `figs/`.
4. Compila (`acl.sty` y `acl_natbib.bst` ya vienen en la plantilla).

## Cómo reproducir los experimentos
Desde la raíz del repositorio:
```bash
python docs/informe/run_experiments.py     # ~15 min; requiere matplotlib
```
Genera `results/*.json` y las figuras `figs/*.{pdf,png}`. Los números son
deterministas (semillas fijas), salvo los tiempos por decisión en milisegundos,
que dependen de la máquina.
