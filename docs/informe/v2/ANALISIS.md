# Experimentos v2 — El Algoritmo Genético sobre la Heurística Mejorada

**Fecha:** 2026-06-10 · **Duración total:** 24.6 min · **Datos:** `results/*.json` · **Figuras:** `figs/*.png|.pdf`

## Pregunta del experimento

> ¿Mejora el rendimiento del Algoritmo Genético si, en lugar de evolucionar los
> 4 pesos de la evaluación Avanzada, evoluciona los **6 pesos de la Heurística
> Mejorada** (que añade amenaza de KO, peligro de KO y cobertura de equipo)?

**Respuesta corta: NO.** El Genético-6 rinde *peor* que el Genético-4 en el
torneo (51.9% vs 54.4% global) y la evaluación de 6 componentes queda **10
puntos por debajo** del techo de la de 4 (54% vs 64% frente al panel). El
detalle y las causas, abajo.

---

## 1. Los agentes y sus funciones de evaluación

Todos los agentes deciden sobre el mismo motor determinista. Lo que cambia es
**qué función de evaluación usan** y **si sus pesos provienen de entrenamiento**.

### 1.1 Aleatorio — sin evaluación
Elige uniformemente entre movimientos y cambios. No tiene función heurística.
**No entrena.** Es la línea base de dificultad del entorno.

### 1.2 Heurística Básica — 1 componente, 1 ply
```
f(s) = hp_ratio(activo propio) − hp_ratio(activo rival)
```
Simula cada acción un nivel y elige la de mayor `f`. **No entrena** (no tiene
pesos). Codiciosa y miope, pero ya supera con holgura al azar (83.8% en este
torneo).

### 1.3 Heurística Avanzada — 4 componentes, 1 ply
```
f(s) = w0·Δvivos + w1·Δhp_equipo + w2·Δtipo + w3·Δvel        (todos en [-1,1])
```
- `Δvivos`: (vivos propios − vivos rival) / 3
- `Δhp_equipo`: **promedio del equipo** propio − rival (no solo el activo)
- `Δtipo`: (mi mejor multiplicador − el suyo) / 4
- `Δvel`: (vel propia − vel rival) / 130

Pesos **fijos ajustados a mano**: `w = (0.40, 0.35, 0.15, 0.10)`. **No cambia
con entrenamiento** en su forma estándar. Esta misma fórmula es la evaluación
de hojas del Minimax y la que el Genético-4 optimiza.

### 1.4 Heurística Mejorada — 6 componentes, 1 ply
```
f(s) = w0·superv + w1·hp_pond + w2·ko_threat + w3·ko_danger + w4·cobertura + w5·vel
```
- `superv`: igual a Δvivos
- `hp_pond`: **0.7·Δhp_del_activo + 0.3·Δhp_promedio_equipo** ← pondera al activo
- `ko_threat`: fracción del HP rival que mi mejor movimiento le quita [0,1]
- `ko_danger`: −(fracción de MI HP que su mejor movimiento me quita), reducido
  a la mitad si soy más rápido [−1,0]
- `cobertura`: mejor multiplicador medio de mi equipo vivo contra el suyo, menos
  el recíproco
- `vel`: igual a Δvel

Pesos **fijos por defecto**: `w = (0.25, 0.20, 0.20, 0.15, 0.10, 0.10)`.
**No cambia con entrenamiento** en su forma estándar; existe la variante
`HeuristicImprovedTrainedAgent` que carga pesos entrenados.

### 1.5 Minimax d=2 (paranoid + poda alfa-beta)
Busca 2 turnos hacia delante; las **hojas se valoran con la fórmula de la
Avanzada** (§1.3) con los mismos pesos fijos `(0.40, 0.35, 0.15, 0.10)`.
Terminales valen ±1. **No entrena.**

### 1.6 Genético-4 — minimax con 4 pesos EVOLUCIONADOS ★ entrena
Mismo agente que §1.5, pero los 4 pesos los optimiza un AG (selección por
torneo k=3, cruce uniforme, mutación gaussiana, elitismo, inmigrantes,
truncamiento 40%, fitness continuo con CRN, panel de rivales, train_depth=1).

**Pesos resultantes de este entrenamiento** (seed 3, 15 gen × pop 16 × 24 bat):
```
(superv, hp, tipo, vel) = (0.262, 0.334, 0.326, 0.078)
```
El AG **triplica el peso del tipo** (0.15→0.33) y reduce supervivencia y
velocidad respecto a los pesos manuales.

### 1.7 Genético-6 — minimax con la evaluación MEJORADA y 6 pesos evolucionados ★ entrena (NUEVO)
`MinimaxImprovedAgent`: la misma búsqueda paranoid + poda alfa-beta, pero las
**hojas se valoran con la fórmula de la Mejorada** (§1.4). El AG evoluciona sus
6 pesos con receta idéntica a la del Genético-4 (misma semilla, mismos
escenarios CRN → comparación justa).

**Pesos resultantes:**
```
(superv, hp_pond, ko+, ko−, cob, vel) = (0.199, 0.174, 0.178, 0.002, 0.136, 0.310)
```
Dos hechos notables: el AG **eliminó por completo `ko_danger`** (0.002 ≈ 0) y
convirtió la **velocidad en el componente dominante** (0.31, vs 0.10 manual).

---

## 2. Exp 0 — Entrenamiento (figura `exp0_fitness`)

| | AG-4 (Avanzada) | AG-6 (Mejorada) |
|---|---|---|
| Win-rate de entrenamiento (vs panel) | **75.0%** | **75.0%** |
| Tiempo de entrenamiento | 46 s | 82 s (~1.8×) |
| Pesos | (0.262, 0.334, 0.326, 0.078) | (0.199, 0.174, 0.178, 0.002, 0.136, 0.310) |

Ambos alcanzan el mismo fitness de entrenamiento, pero eso mide solo los 24
escenarios de entrenamiento; la generalización se mide abajo.

## 3. Exp A — Torneo de 7 agentes (80 batallas/par, figura `expA_torneo`)

Win-rate global (IC 95% Wilson, 480 batallas por agente):

| Agente | Global | IC 95% |
|---|---|---|
| **H. Avanzada** | **61.5%** | [57.0, 65.7] |
| H. Mejorada | 57.9% | [53.5, 62.3] |
| H. Básica | 56.2% | [51.8, 60.6] |
| Genético-4 | 54.4% | [49.9, 58.8] |
| **Genético-6** | **51.9%** | [47.4, 56.3] |
| Minimax-d2 | 47.3% | [42.9, 51.8] |
| Random | 20.8% | [17.4, 24.7] |

- **Genético-6 < Genético-4** (51.9 vs 54.4; IC solapados pero la dirección es
  consistente con el resto de evidencia). El duelo directo quedó **50.0%–50.0%**.
- La **H. Avanzada sigue siendo el mejor agente** (61.5%), y le gana al
  Genético-6 con su margen más amplio contra un agente informado (61.3%).
- Ambos genéticos superan al Minimax de pesos manuales (58.8% y 51.2% en
  duelo directo): **evolucionar pesos sí ayuda al minimax**, solo que la
  evaluación de 6 componentes no es mejor punto de partida.
- Duración media 11.7 turnos, 0% de empates.

## 4. Exp B — Profundidad, poda y coste de la evaluación (figura `expB_poda_coste`)

Coste de búsqueda (40 posiciones):

| d | Nodos (poda) | Nodos (sin) | Reducción | ms/dec eval-4 | ms/dec eval-6 |
|---|---|---|---|---|---|
| 1 | 42.0 | 42.0 | 0% | 0.63 | 1.35 |
| 2 | 742.9 | 1 549.0 | **52.0%** | 9.98 | 30.71 |
| 3 | 10 366.3 | 55 017.7 | **81.2%** | 125.8 | 422.4 |

- La poda replica el resultado v1 (≈50%/80% de ahorro creciendo con d).
- **La evaluación de 6 componentes cuesta ~3× dentro del minimax** (30.7 vs
  10.0 ms en d=2; 422 vs 126 ms en d=3): el coste extra de ko_threat/ko_danger/
  cobertura se paga en *cada hoja*.

Win-rate Minimax (eval-4, pesos manuales) vs Básica: d1 52.5% [41.7,63.1],
d2 52.5% [41.7,63.1], d3 38.8% [28.8,49.7]. La profundidad sigue sin mejorar
el win-rate (esta corrida d3 salió incluso peor; los IC son anchos).

## 5. Exp C — Elitismo en el AG-6 (3 semillas, figura `expC_elitismo`)

| elite_k | 0 | 2 | 4 |
|---|---|---|---|
| Fitness final (media ± desv.) | 65.9% ± 7.3 | 63.9% ± 9.3 | 63.9% ± 9.3 |

Igual que en v1: **diferencias pequeñas y solapadas, sin ventaja clara del
elitismo** a esta escala. (Nota: aquí "fitness" es el fitness continuo de
selección, no win-rate.)

## 6. Exp D — Variantes (figura `expD_variantes`)

**D1 — Expectimax vs Minimax paranoid** (60 batallas/rival): Expectimax global
56.1% [48.8,63.2] vs Minimax 53.3% [46.1,60.5]; directo 51.7% pro-Expectimax.
Replica v1: mejora leve, no significativa.

**D2 — Generalización del AG-6** (entrenado vs 1 rival o vs panel):

| Fitness entrenado contra | Random | Básica | Avanzada | **Minimax-d2 (no visto)** | Global |
|---|---|---|---|---|---|
| 1 rival (Básica) | 75.0 | 55.0 | 38.3 | **43.3** | 52.9 |
| Panel (R+B+A) | 63.3 | 43.3 | 48.3 | **60.0** | 53.8 |

El patrón de v1 se replica exactamente con la nueva evaluación: **entrenar
contra el panel generaliza mucho mejor al rival no visto** (+16.7 puntos contra
Minimax-d2), a costa de rendimiento contra los rivales del fitness ajeno.
El sobreajuste es propiedad del *fitness*, no de la evaluación.

## 7. Exp E — Robustez y techo de la evaluación (figura `expE_techo`) ⭐ el hallazgo central

**E1 — Robustez del AG-6** (5 corridas/config, evaluado en 150 escenarios):

| Config | mín | media | máx |
|---|---|---|---|
| Sin inmigrantes | 50.0 | 50.9 | 54.7 |
| Con inmigrantes | **54.0** | **54.8** | 56.0 |

Los inmigrantes vuelven a elevar piso y media (+4 puntos) — la receta de
diversidad funciona igual sobre la evaluación de 6 componentes.

**E2 — Techo de la evaluación, 4 vs 6 pesos** (mismos 150 escenarios para todos):

| Configuración | Pesos | d=1 | d=2 |
|---|---|---|---|
| default-4 | (0.40,0.35,0.15,0.10) | 54.0 | 54.7 |
| genético-4 | (0.262,0.334,0.326,0.078) | **59.3** | 56.0 |
| **soloHP-4** | (0,1,0,0) | **64.0** | **64.0** |
| default-6 | (0.25,0.20,0.20,0.15,0.10,0.10) | 48.7 | 54.0 |
| genético-6 | (0.199,0.174,0.178,0.002,0.136,0.310) | 54.0 | 51.3 |
| soloHP-6 | (0,1,0,0,0,0) | 46.7 | 49.3 |

Lecturas clave:

1. **El techo de ~64% sigue siendo de la familia de 4 pesos** (soloHP-4 lo
   alcanza en ambas profundidades, replicando v1 exactamente).
2. **La mejor configuración de 6 pesos (54.0%) queda 10 puntos por debajo del
   techo de 4** — la evaluación más rica no solo no rompe el techo: *no llega*.
3. El detalle más revelador: **soloHP-6 (46.7/49.3) ≪ soloHP-4 (64/64)** pese a
   que ambos ponderan "solo HP". La razón es estructural: el componente de HP
   de la Mejorada es `hp_pond = 0.7·Δhp_activo + 0.3·Δhp_equipo`, sesgado hacia
   el Pokémon **activo**, mientras que el de la Avanzada es el **promedio del
   equipo completo**. El HP de equipo es la señal dominante del dominio; al
   diluirla con el HP del activo (volátil, cambia con cada switch), la
   evaluación pierde justo la información que más predice la victoria.

**E3 — Avanzada vs Mejorada a 1 nivel** (150 batallas, replicación de v1):
Avanzada 63.3% vs Básica y 87.3% vs Random (0.12 ms/dec); Mejorada 58.0% y
82.0% (0.37 ms/dec, ~3×); directo Mejorada 45.3%. Confirmado de nuevo: los 6
componentes no aportan win-rate ni a 1 ply ni dentro del minimax.

---

## 8. Interpretación global

**La hipótesis "el genético con la Heurística Mejorada tendrá mejor rendimiento"
queda refutada por tres vías independientes:**

1. **Torneo** (Exp A): Genético-6 51.9% < Genético-4 54.4%; empate 50/50 directo.
2. **Techo** (E2): la familia de 6 pesos rinde sistemáticamente por debajo de la
   de 4 con cualquier vector probado (manual, evolucionado, solo-HP).
3. **Coste** (Exp B): además rinde menos pagando ~3× más cómputo por decisión.

**¿Por qué pierde la evaluación "más inteligente"?**

- **Doble contabilidad táctica.** `ko_threat` y `ko_danger` son señales de
  1 turno. Dentro de un minimax d=2 la búsqueda *ya simula* esos intercambios:
  añadirlos en la hoja cuenta dos veces la táctica inmediata y diluye la señal
  estratégica (HP de equipo) que decide las partidas. Es coherente con que el
  propio AG haya **anulado ko_danger (peso 0.002)**: la evolución "descubrió"
  que ese componente estorba.
- **El componente de HP está mal orientado para este dominio.** El 70% de
  `hp_pond` mira al activo; soloHP-6 (46.7%) vs soloHP-4 (64%) lo demuestra
  directamente.
- **El dominio es simple a propósito** (sin estados de alteración ni
  físico/especial): no hay margen táctico extra que una evaluación más rica
  pueda explotar. Esto refuerza la conclusión v1 del *techo estructural*: el
  cuello de botella es el motor, no la evaluación ni el optimizador.

**Lo que sí se sostiene (se replica en v2 con la nueva evaluación):**
- La poda alfa-beta ahorra 52–81% de nodos sin cambiar la decisión.
- El fitness contra panel generaliza mejor que contra un rival (+16.7 pts vs
  rival no visto).
- Los inmigrantes elevan el piso del AG (+4 pts) y reducen varianza.
- El elitismo sigue sin mostrar ventaja a esta escala.
- La H. Avanzada (4 componentes, pesos manuales) sigue siendo el mejor agente.

**Valor para el informe:** este resultado negativo es publicable y didáctico:
*más componentes ≠ mejor evaluación*. Una función de evaluación debe aportar
información **complementaria a la búsqueda** (estratégica, de largo plazo), no
duplicar lo que la búsqueda ya calcula (táctica de corto plazo). Conecta con la
literatura clásica: las evaluaciones de ajedrez fuertes son simples y dejan la
táctica al árbol.

## 9. Configuración reproducible

- Script: `docs/informe/v2/run_experiments_v2.py` (desde la raíz:
  `python docs/informe/v2/run_experiments_v2.py`)
- Semillas: entrenamiento 3 (ambos AG, CRN), torneo 101, posiciones B 202,
  elitismo {1,2,3}, D 404/7, E1 1, escenarios de evaluación 777/42/43/44.
- Pesos entrenados guardados en `data/genetic_g15_p16_d2.json` (4) y
  `data/genetic_improved_g15_p16_d2.json` (6).
- Log completo de la corrida: `run_log.txt`.
