# Informe PokeFisi (formato ACL)

Informe en LaTeX siguiendo la plantilla oficial de la *Association for
Computational Linguistics* (ACL).

## Archivos
- `main.tex` — documento principal (español, formato ACL).
- `custom.bib` — bibliografía.
- `figs/` — figuras generadas por los experimentos (PDF).
- `run_experiments.py` — Experimentos A–C: torneo, profundidad/poda, elitismo (+ figuras).
- `run_variants.py` — Experimento D: variantes (expectimax, panel de rivales).
- `run_experiment_E.py` — Experimento E: refinamiento del genético, techo del eval, Avanzada vs Mejorada.
- `results.json`, `results_variants.json`, `results_E.json` — resultados numéricos de cada bloque.

## Cómo compilar (Overleaf, recomendado)
1. Abre la plantilla ACL: <https://www.overleaf.com/latex/templates/association-for-computational-linguistics-acl-conference/jvxskxpnznfj>.
2. Reemplaza el `main.tex` de la plantilla por este `main.tex`.
3. Sube `custom.bib` y la carpeta `figs/`.
4. Compila (los archivos de estilo `acl.sty` y `acl_natbib.bst` ya vienen en la plantilla).

## Cómo reproducir los experimentos
Desde la raíz del repositorio:
```bash
python docs/informe/run_experiments.py     # A–C (figuras; requiere matplotlib)
python docs/informe/run_variants.py        # D (variantes)
python docs/informe/run_experiment_E.py    # E (refinamiento del genético; ~6 min)
```
Cada script guarda su `results_*.json`; `run_experiments.py` además genera las
figuras en `figs/`.
