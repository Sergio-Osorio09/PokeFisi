# Expectimax — Búsqueda que modela al rival

`ExpectimaxAgent` (`ai/expectimax_agent.py`) es una variante de búsqueda adversaria, **subclase de `MinimaxAgent`**. Comparte la función de evaluación (los 4 diferenciales), la simulación de turno y el panel "cerebro"; solo cambia **cómo trata al rival**.

## La idea

- El **Minimax (paranoid)** asume que el rival juega para **minimizar tu evaluación** (el peor caso).
- El **Expectimax** **no** asume el peor caso: **modela** al rival con una política concreta (por defecto la **Heurística Básica**) y desciende por **la jugada que el rival realmente elegiría** — una sola, no todas.

> Nota: el Expectimax *de los libros* promedia sobre nodos de azar (esperanza matemática). El de PokeFisi colapsa al rival a su jugada predicha (no promedia) → es más bien un "max contra un rival con política fija".

## Diferencias con Minimax

| | **Minimax (α-β)** | **Expectimax (contra-modelo)** |
|---|---|---|
| Supuesto del rival | peor caso (minimiza mi eval) | modelo fijo predice **1** jugada |
| Ramifica sobre | mis acciones × las del rival | **solo mis** acciones (el rival = 1 nodo) |
| Poda α-β | sí | no (no hay nodos MIN que podar) |
| Carácter | pesimista, robusto | realista vs el modelo; *explotable* si el modelo falla |

## Complejidad

Con `b` = factor de ramificación (movimientos + cambios, ~4-7) y `d` = profundidad (turnos):

- **Minimax** sin poda: `O(b^{2d})`; con poda α-β (mejor caso): `~O(b^{d})`.
- **Expectimax**: `~O(b^{d})` × costo del modelo por nodo. El rival no se ramifica → árbol **mucho más angosto**, pero paga consultar al modelo en cada nodo.

## Comportamiento observado (banco de pruebas)

A profundidad 2, Expectimax es **~3.5× más rápido** que Minimax (≈3 ms vs ≈11 ms por jugada), pero **gana menos** (≈43% vs ≈59%).

El motivo: su modelo del rival (Heurística Básica) **no acierta** con la variedad de rivales reales del torneo; **cuando el modelo se equivoca, el Expectimax pierde su ventaja**, mientras el pesimismo del Minimax resulta más robusto. Es un buen ejemplo del **trade-off costo/calidad** y de la **dependencia del modelo del oponente**.

Ver también [`minimax.md`](minimax.md) y el panel de razonamiento en [`panel_cerebro_ia.md`](panel_cerebro_ia.md).
