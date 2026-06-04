# Informe PokeFisi (formato ACL)

Informe en LaTeX siguiendo la plantilla oficial de la *Association for
Computational Linguistics* (ACL).

## Archivos
- `main.tex` — documento principal (español, formato ACL).
- `custom.bib` — bibliografía.
- `figs/` — figuras generadas por los experimentos (PDF).
- `run_experiments.py` — script que genera los datos y las figuras.
- `results.json` — resultados numéricos de la última ejecución.

## Cómo compilar (Overleaf, recomendado)
1. Abre la plantilla ACL: <https://www.overleaf.com/latex/templates/association-for-computational-linguistics-acl-conference/jvxskxpnznfj>.
2. Reemplaza el `main.tex` de la plantilla por este `main.tex`.
3. Sube `custom.bib` y la carpeta `figs/`.
4. Compila (los archivos de estilo `acl.sty` y `acl_natbib.bst` ya vienen en la plantilla).

## Cómo reproducir los experimentos
Desde la raíz del repositorio:
```bash
python docs/informe/run_experiments.py
```
Genera `results.json` y las figuras en `figs/`. Requiere `matplotlib`.
