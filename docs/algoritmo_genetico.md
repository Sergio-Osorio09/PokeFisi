# Algoritmo Genético — Optimización del Minimax (poda alfa-beta)

## ¿Qué es un Algoritmo Genético?

Un **Algoritmo Genético (AG)** es una técnica de optimización inspirada en la evolución biológica. En lugar de buscar la solución óptima con fórmulas matemáticas, el AG simula la selección natural:

> Las soluciones malas desaparecen. Las buenas se reproducen y se mezclan entre sí. Las mejores sobreviven generación tras generación.

No se necesita saber de antemano cómo es la solución óptima — el algoritmo la encuentra explorando y seleccionando automáticamente.

---

## El problema que resuelve en PokeFisi

El `MinimaxAgent` (búsqueda con poda alfa-beta) evalúa cada estado de batalla
con la misma función de cuatro componentes que la Heurística Avanzada:

```
score = w0 * supervivencia  +  w1 * hp_diff  +  w2 * tipo  +  w3 * velocidad
```

Los **pesos** `[w0, w1, w2, w3]` determinan qué tan importante es cada factor en
las hojas del árbol minimax. Por defecto son `[0.40, 0.35, 0.15, 0.10]`, definidos
a mano. El AG encuentra automáticamente cuáles pesos hacen que el **Minimax** gane
más batallas: cada individuo se mide jugando con un `MinimaxAgent` que usa esos pesos.

> **Nota de costo:** evaluar con minimax es mucho más caro que con la heurística
> directa (el minimax expande un árbol de varios turnos por decisión). Por eso los
> valores por defecto del AG son más conservadores: `pop_size=12`, `generations=15`,
> `battles_per_eval=6`, `minimax_depth=2`.

---

## Vocabulario fundamental

| Término biológico | Equivalente en PokeFisi |
|---|---|
| **Cromosoma / Individuo** | Un vector de 4 pesos `[w0, w1, w2, w3]` |
| **Gen** | Un peso individual (ej. `w2 = 0.18`) |
| **Población** | Conjunto de N individuos (ej. 20 vectores de pesos distintos) |
| **Fitness** | Win-rate del individuo al jugar K batallas |
| **Selección** | Preferir los individuos con mayor win-rate como padres |
| **Crossover** | Combinar dos individuos para crear un hijo |
| **Mutación** | Alterar levemente un gen al azar |
| **Generación** | Una iteración completa del ciclo evolutivo |
| **Élite** | Los mejores N individuos que pasan intactos a la siguiente generación |

---

## Arquitectura del código

```
ai/
├── genetic_trainer.py     ← Todo el algoritmo genético (funciones puras)
├── genetic_agent.py       ← GeneticAgent: subclase de MinimaxAgent con pesos evolucionados
├── minimax_agent.py       ← MinimaxAgent: acepta `weights` que el AG inyecta en su evaluación
data/
└── genetic_g15_p12_d2.json ← Pesos guardados (g=generaciones, p=población, d=profundidad)
```

---

## Paso a paso: qué ocurre en cada generación

### Generación 0 — Inicialización

Se crean N individuos completamente al azar. Cada individuo es un vector de 4 números positivos normalizados (suman 1.0).

```python
# Ejemplo con N=4 para ilustrar (en práctica N=20)
Individuo 1: [0.52, 0.21, 0.19, 0.08]  # favorece supervivencia
Individuo 2: [0.15, 0.60, 0.10, 0.15]  # favorece HP
Individuo 3: [0.25, 0.25, 0.35, 0.15]  # favorece tipo
Individuo 4: [0.30, 0.20, 0.10, 0.40]  # favorece velocidad
```

Ninguno sabe todavía qué tan bueno es. El AG lo descubrirá evaluando.

---

### Paso 1 — Evaluación de Fitness

Cada individuo se inyecta como los pesos de un `MinimaxAgent` y juega **K batallas**
contra `HeuristicaBasica`. Su fitness es su win-rate.

```
Individuo 1: juega 10 batallas → gana 7  → fitness = 0.70
Individuo 2: juega 10 batallas → gana 4  → fitness = 0.40
Individuo 3: juega 10 batallas → gana 8  → fitness = 0.80  ← mejor
Individuo 4: juega 10 batallas → gana 5  → fitness = 0.50
```

**¿Por qué contra HeuristicaBasica?** Es suficientemente competente para distinguir pesos buenos de malos, pero lo bastante débil para que un buen conjunto de pesos lo venza con claridad.

---

### Paso 2 — Elitismo

Los **top-K mejores** individuos pasan directamente a la siguiente generación sin cambios. Esto garantiza que la mejor solución encontrada **nunca se pierde**.

```
Elite (K=2):
  Individuo 3: [0.25, 0.25, 0.35, 0.15]  fitness=0.80  → pasa intacto
  Individuo 1: [0.52, 0.21, 0.19, 0.08]  fitness=0.70  → pasa intacto
```

---

### Paso 3 — Selección por torneo

Para generar el resto de hijos se elige a los **padres por torneo**:
1. Se seleccionan 3 individuos al azar de la población
2. Gana el de mayor fitness
3. Ese es el padre (o madre)
4. Se repite para el segundo padre

```
Torneo para Padre A:
  Candidatos: Individuo 1 (0.70), Individuo 4 (0.50), Individuo 2 (0.40)
  Ganador: Individuo 1 → Padre A = [0.52, 0.21, 0.19, 0.08]

Torneo para Padre B:
  Candidatos: Individuo 3 (0.80), Individuo 2 (0.40), Individuo 4 (0.50)
  Ganador: Individuo 3 → Padre B = [0.25, 0.25, 0.35, 0.15]
```

Los torneos favorecen a los buenos pero permiten que los menos buenos participen — esto mantiene diversidad genética.

---

### Paso 4 — Crossover uniforme

Se mezclan los genes de ambos padres. Por cada posición, se lanza una moneda: si cae cara → gen del Padre A, si cae cruz → gen del Padre B.

```
Padre A: [0.52, 0.21, 0.19, 0.08]
Padre B: [0.25, 0.25, 0.35, 0.15]
Moneda:  [ A,    B,    B,    A  ]
         ↓
Hijo:    [0.52, 0.25, 0.35, 0.08]   (sin normalizar aún)
```

El hijo hereda rasgos de ambos padres — potencialmente combinando lo mejor de cada uno.

---

### Paso 5 — Mutación gaussiana

Con probabilidad `mutation_rate` (15% por gen), se perturba ligeramente el valor:

```python
perturbación = ruido gaussiano con σ = mutation_strength (0.10)
```

```
Hijo antes:  [0.52, 0.25, 0.35, 0.08]
Gen 0 muta:  0.52 + gauss(0, 0.10) = 0.52 + 0.07  = 0.59
Gen 2 muta:  0.35 + gauss(0, 0.10) = 0.35 + (-0.04) = 0.31
Hijo después:[0.59, 0.25, 0.31, 0.08]
```

La mutación introduce **variación novedosa** que el crossover solo no puede crear. Sin mutación, el AG converge prematuramente hacia un óptimo local.

---

### Paso 6 — Normalización

Después de crossover y mutación los pesos pueden no sumar 1. Se normalizan:

```
[0.59, 0.25, 0.31, 0.08]  →  suma = 1.23
Normalizado: [0.48, 0.20, 0.25, 0.07]   (cada uno ÷ 1.23)
```

---

### Fin de generación — Nueva población

```
Nueva generación:
  [ELITE]  Individuo 3: [0.25, 0.25, 0.35, 0.15]  (sin cambios)
  [ELITE]  Individuo 1: [0.52, 0.21, 0.19, 0.08]  (sin cambios)
  [HIJO 1] [0.48, 0.20, 0.25, 0.07]               (del cruce anterior)
  [HIJO 2] ...                                     (otros cruces)
```

Este proceso se repite por **G generaciones**. Con cada ciclo, la población tiende a converger hacia pesos que producen mayor win-rate.

---

## Evolución típica a lo largo de las generaciones

```
Gen  1/30  |  Mejor gen: ████████░░ 80%  |  Mejor global: ████████░░ 80%  |  Promedio: 58%
Gen  2/30  |  Mejor gen: ███████░░░ 70%  |  Mejor global: ████████░░ 80%  |  Promedio: 62%
Gen  3/30  |  Mejor gen: █████████░ 90%  |  Mejor global: █████████░ 90%  |  Promedio: 67%
Gen  4/30  |  Mejor gen: ████████░░ 80%  |  Mejor global: █████████░ 90%  |  Promedio: 71%
...
Gen 15/30  |  Mejor gen: █████████░ 90%  |  Mejor global: █████████░ 90%  |  Promedio: 78%
Gen 20/30  |  Mejor gen: ██████████100%  |  Mejor global: ██████████100%  |  Promedio: 82%
...
Gen 30/30  |  Mejor gen: █████████░ 90%  |  Mejor global: ██████████100%  |  Promedio: 85%
```

**Observaciones típicas:**
- Las primeras generaciones tienen alta varianza — hay individuos muy buenos y muy malos
- El promedio sube progresivamente a medida que los malos son eliminados
- El "mejor global" solo puede subir o mantenerse (nunca baja — lo garantiza el elitismo)
- El "mejor de la generación" puede bajar si los hijos de esta gen son peores que el récord anterior
- Después de ~20 generaciones la población converge y los saltos se vuelven raros

---

## Parámetros y su efecto

| Parámetro | Valor por defecto | Efecto si sube | Efecto si baja |
|---|---|---|---|
| `pop_size` | 12 | Más diversidad, más lento | Converge más rápido, riesgo de estancarse |
| `generations` | 15 | Más refinamiento | Menos exploración |
| `battles_per_eval` | 6 | Fitness más preciso, más lento | Rápido pero ruidoso |
| `minimax_depth` | 2 | Minimax más fuerte y mucho más lento por batalla | Más rápido, búsqueda más superficial |
| `mutation_rate` | 15% | Más exploración, menos estabilidad | Converge rápido, poco novedoso |
| `mutation_strength` | 0.10 | Cambios más grandes | Ajuste fino |
| `elite_k` | 2 | Más conservador | Más riesgo de perder el mejor |

**Regla práctica:** Si el AG converge muy rápido sin mejorar, subir `mutation_rate`. Si no converge nunca, bajarlo.

---

## Cómo usar desde la consola

```
POKEFISI - Consola
  4. Entrenar IA Genetica
```

Al elegir la opción 4, se pedirán los parámetros y se mostrará el progreso generación a generación:

```
=== Entrenar IA Genetica ===

  Tamaño de poblacion (min. 4) [12]: 12
  Numero de generaciones (min. 5) [15]: 15
  Batallas por evaluacion (min. 5) [6]: 6
  Profundidad del Minimax (2 o 3) [2]: 2

  Configuracion:
    Poblacion         : 12 individuos
    Generaciones      : 15
    Batallas/individuo: 6
    Profundidad Minimax: 2 turno(s)
    Total evaluaciones: 1080 batallas aprox.

  Iniciando evolucion...

  Gen   1/15  |  Mejor gen: ████████░░ 80%  |  ...
  Gen   2/15  |  ...
  ...
  Gen  15/15  |  ...

  Evolucion completada!
  Guardado en: data/genetic_g15_p12_d2.json
  Fitness final: 90%

  Pesos evolucionados vs base:
    supervivencia   0.3821  (base 0.400,  -0.0179)
    hp_diff         0.4103  (base 0.350,  +0.0603)
    tipo            0.1342  (base 0.150,  -0.0158)
    velocidad       0.0734  (base 0.100,  -0.0266)
```

---

## Cómo leer los resultados

Ejemplo de pesos evolucionados vs base:

```
supervivencia:  0.38  (base 0.40)  — ligeramente menos importante
hp_diff:        0.41  (base 0.35)  ↑ más importante: el AG descubrió que el HP es clave
tipo:           0.13  (base 0.15)  — similar
velocidad:      0.07  (base 0.10)  ↓ menos importante en la práctica
```

**Interpretación:** El AG encontró que en batallas 3v3 con stats nivel 100, la diferencia de HP acumulada importa más que la ventaja de tipo. Los Pokémon sobreviven más turnos, por lo que el desgaste por HP es determinante.

---

## Formato del archivo guardado

`data/genetic_g15_p12_d2.json`:

```json
{
  "weights": [0.38, 0.41, 0.13, 0.07],
  "fitness": 0.90,
  "generations": 15,
  "pop_size": 12,
  "battles_per_eval": 6,
  "minimax_depth": 2,
  "mutation_rate": 0.15,
  "mutation_strength": 0.10,
  "elite_k": 2,
  "history": [
    {"gen": 1, "best_gen": 0.80, "best_global": 0.80, "avg": 0.58, "best_weights": [...]},
    {"gen": 2, "best_gen": 0.70, "best_global": 0.80, "avg": 0.62, "best_weights": [...]},
    ...
  ]
}
```

El campo `history` permite graficar la curva de evolución post-entrenamiento.

---

## Diferencias con el entrenador por hill-climbing (opción 3)

| Característica | Heurística entrenada (opción 3) | IA Genética (opción 4) |
|---|---|---|
| Algoritmo | Hill-climbing / búsqueda local | Algoritmo Genético |
| Agente optimizado | HeuristicaAvanzada (evaluación 1 ply) | Minimax (poda alfa-beta, varios turnos) |
| Población | 1 individuo | N individuos en paralelo |
| Exploración | Local (un paso a la vez) | Global (toda la población) |
| Riesgo de óptimo local | Alto | Bajo (la diversidad lo evita) |
| Velocidad | Rápido | Más lento (evalúa N×G individuos) |
| Calidad de resultado | Buena para ajuste fino | Mejor para exploración amplia |

---

## Pseudocódigo completo

```
INICIALIZAR población con N individuos aleatorios

PARA gen EN 1..G:
    PARA cada individuo:
        # el individuo son los pesos de un MinimaxAgent(depth=D)
        fitness[i] = win_rate(Minimax(pesos=individuo[i]), K batallas vs panel de rivales)

    mejor_gen    = individuo con mayor fitness esta generación
    mejor_global = max(mejor_global, mejor_gen)   # nunca retrocede

    MOSTRAR progreso de gen

    nueva_pop = elite_k mejores individuos (sin cambios)

    MIENTRAS len(nueva_pop) < N:
        padre_A = torneo(3 candidatos aleatorios)
        padre_B = torneo(3 candidatos aleatorios)
        hijo    = crossover_uniforme(padre_A, padre_B)
        hijo    = mutar(hijo, rate=0.15, σ=0.10)
        hijo    = normalizar(hijo)
        nueva_pop.agregar(hijo)

    población = nueva_pop

GUARDAR mejor_global en data/genetic_*.json
```
