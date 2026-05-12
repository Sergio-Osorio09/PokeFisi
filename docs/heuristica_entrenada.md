# Heurística Entrenada — Optimización por Hill-Climbing

## ¿Qué es el Hill-Climbing?

El **Hill-Climbing** (escalada de colinas) es una técnica de búsqueda local que mejora una solución paso a paso, moviéndose siempre hacia la dirección que la mejora.

La metáfora es literal: imagina que estás en un paisaje montañoso con los ojos vendados. Para llegar a la cima, siempre das un paso hacia donde el terreno sube. No puedes ver el mapa completo — solo sientes si el siguiente paso sube o baja.

```
            Óptimo global
                ▲
           ▲   /|\
          /|\ / | \
         / | X  |  \   ← Óptimo local (riesgo del hill-climbing)
        /  |/ \ |   \
───────/───┼───\┼────\───
    Inicio        Fin
```

El problema: si llegas a un óptimo local, el algoritmo se detiene aunque exista una cima más alta en otra parte del paisaje.

---

## El problema que resuelve en PokeFisi

La `HeuristicaAvanzada` usa 4 pesos `[w0, w1, w2, w3]`. El entrenador los ajusta automáticamente jugando batallas reales, buscando la combinación que gana más.

**¿Qué se optimiza?** El **win-rate** (porcentaje de victorias) contra una mezcla de rivales: 50% contra el Agente Aleatorio y 50% contra la Heurística Básica.

---

## Vocabulario fundamental

| Término | Equivalente en PokeFisi |
|---|---|
| **Solución actual** | El vector de pesos `[w0, w1, w2, w3]` en uso |
| **Candidato** | Un nuevo vector de pesos generado perturbando el actual |
| **Fitness / Calidad** | Win-rate acumulado del vector de pesos |
| **Temperatura** | Tamaño de la perturbación (grande al inicio, pequeña al final) |
| **Ventana** | Las últimas 20 batallas usadas para medir el win-rate reciente |

---

## Arquitectura del código

```
ai/
├── trainer.py          ← Bucle de entrenamiento hill-climbing
├── heuristic_trained.py ← Agente que carga los pesos entrenados
data/
└── weights_N.json      ← Pesos guardados tras entrenar N batallas
```

---

## Paso a paso: qué ocurre en cada batalla de entrenamiento

### Inicialización

Se empieza con los pesos por defecto de la Heurística Avanzada:

```
pesos_actuales = [0.40, 0.35, 0.15, 0.10]
pesos_mejores  = [0.40, 0.35, 0.15, 0.10]
mejor_win_rate = 0.0
```

---

### Paso 1 — Generar un candidato con temperatura decreciente

La **temperatura** controla cuánto se perturban los pesos. Al inicio es grande (exploración amplia), al final es pequeña (ajuste fino):

```python
temperatura = 0.12 × e^(-3.5 × i / n_batallas)
```

```
Batalla   1/100:  temperatura ≈ 0.120  (cambios grandes, exploración)
Batalla  25/100:  temperatura ≈ 0.062  (cambios medianos)
Batalla  50/100:  temperatura ≈ 0.032  (cambios pequeños)
Batalla  75/100:  temperatura ≈ 0.016  (ajuste fino)
Batalla 100/100:  temperatura ≈ 0.008  (micro-ajustes)
```

Los pesos candidatos se generan añadiendo ruido gaussiano:

```
pesos_actuales = [0.40, 0.35, 0.15, 0.10]
temperatura    = 0.06

Ruido gaussiano (σ = temperatura):
  w0 += gauss(0, 0.06) = +0.03  →  0.43
  w1 += gauss(0, 0.06) = -0.02  →  0.33
  w2 += gauss(0, 0.06) = +0.01  →  0.16
  w3 += gauss(0, 0.06) = -0.01  →  0.09

Candidato (antes de normalizar): [0.43, 0.33, 0.16, 0.09]
```

Luego se normalizan para que sumen 1.0:

```
Suma = 0.43 + 0.33 + 0.16 + 0.09 = 1.01
Candidato normalizado: [0.426, 0.327, 0.158, 0.089]
```

---

### Paso 2 — Jugar una batalla con el candidato

Se construyen equipos aleatorios de 3 Pokémon y se enfrenta el candidato contra:
- **50% de las batallas**: Agente Aleatorio (batallas pares)
- **50% de las batallas**: Heurística Básica (batallas impares)

```
Batalla 0 → vs Aleatorio
Batalla 1 → vs Básica
Batalla 2 → vs Aleatorio
...
```

Esta mezcla asegura que los pesos aprendidos funcionen contra oponentes de distinta dificultad.

---

### Paso 3 — Actualizar si el candidato ganó

El hill-climbing puro solo acepta mejoras:

```
SI el candidato ganó:
    pesos_actuales = candidato  ← nos movemos a la nueva posición
SINO:
    pesos_actuales permanece igual  ← nos quedamos donde estamos
```

A diferencia del Algoritmo Genético, **no hay población**: solo una solución que se mueve paso a paso.

---

### Paso 4 — Trackear el mejor con ventana deslizante

Para medir la calidad sin depender de una sola batalla (muy ruidosa), se usa una **ventana de las últimas 20 batallas**:

```
Ventana (últimas 20): [1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0]
Win-rate ventana = 14/20 = 70%

Si 70% ≥ mejor_win_rate_hasta_ahora Y ventana tiene ≥ 10 batallas:
    mejor_win_rate = 70%
    pesos_mejores  = pesos_actuales
```

Los **pesos guardados** son los que tuvieron el mejor win-rate en ventana, no necesariamente los últimos.

---

### Progreso en consola

```
=== Entrenar Heuristica Avanzada ===
¿Cuantas batallas para entrenar? (min. 10): 100

Entrenando 100 batallas vs Random (50%) y HeuristicBasica (50%)...

 [ 10%] Batalla  10/100  |  Win-rate: 0.600  |  Temp: 0.0957
 [ 20%] Batalla  20/100  |  Win-rate: 0.650  |  Temp: 0.0764
 [ 30%] Batalla  30/100  |  Win-rate: 0.633  |  Temp: 0.0610
 [ 40%] Batalla  40/100  |  Win-rate: 0.625  |  Temp: 0.0487
 [ 50%] Batalla  50/100  |  Win-rate: 0.640  |  Temp: 0.0389
 [ 60%] Batalla  60/100  |  Win-rate: 0.650  |  Temp: 0.0311
 [ 70%] Batalla  70/100  |  Win-rate: 0.657  |  Temp: 0.0248
 [ 80%] Batalla  80/100  |  Win-rate: 0.663  |  Temp: 0.0198
 [ 90%] Batalla  90/100  |  Win-rate: 0.667  |  Temp: 0.0158
 [100%] Batalla 100/100  |  Win-rate: 0.670  |  Temp: 0.0126

Entrenamiento completado!
Guardado en: data/weights_100.json
Win-rate: 67.0%

Pesos aprendidos:
  supervivencia   0.3821  (base 0.400,  -0.0179)
  hp_diff         0.4103  (base 0.350,  +0.0603)
  tipo            0.1342  (base 0.150,  -0.0158)
  velocidad       0.0734  (base 0.100,  -0.0266)
```

---

## Por qué la temperatura decrece (Simulated Annealing light)

La técnica de temperatura decreciente está inspirada en el **Simulated Annealing** (recocido simulado). La diferencia es que el SA completo también acepta soluciones peores con cierta probabilidad (para escapar de óptimos locales). Este entrenador usa solo la parte de temperatura sin aceptar peores soluciones.

**Intuición:**
- Al inicio exploras amplio: das pasos grandes para encontrar zonas prometedoras
- Al final explotas fino: das pasos pequeños para perfeccionar la mejor zona encontrada

```
Inicio:  [0.40, 0.35, 0.15, 0.10] → genera [0.52, 0.28, 0.09, 0.11] (diferente)
Final:   [0.41, 0.38, 0.13, 0.08] → genera [0.412, 0.381, 0.129, 0.078] (casi igual)
```

---

## Formato del archivo guardado

`data/weights_100.json`:

```json
{
  "weights": [0.3821, 0.4103, 0.1342, 0.0734],
  "battles": 100,
  "win_rate": 0.67
}
```

El nombre del archivo incluye el número de batallas usadas: `weights_100.json`, `weights_500.json`, etc. Si entrenas con más batallas, el archivo nuevo coexiste con el anterior.

---

## Diferencias con el Algoritmo Genético

| Característica | Heurística Entrenada (Hill-Climbing) | IA Genética (AG) |
|---|---|---|
| Soluciones simultáneas | 1 (una sola solución) | N (toda una población) |
| Exploración | Local (un paso a la vez) | Global (toda la población) |
| Riesgo de óptimo local | Alto | Bajo |
| Velocidad | Muy rápido | Más lento (N×G evaluaciones) |
| Con pocas batallas | Buena aproximación | Necesita más evaluaciones |
| Con muchas batallas | Puede estancarse | Sigue mejorando |

**Regla práctica:** Para ajuste rápido con pocas batallas (10–200), usa el entrenador. Para búsqueda exhaustiva con paciencia, usa el Genético.

---

## Cómo usar desde la consola

```
POKEFISI - Consola
  3. Entrenar Heuristica Avanzada
```

Se pide el número de batallas de entrenamiento (mínimo 10) y el proceso comienza. Los pesos resultantes quedan disponibles automáticamente en el selector de IAs de la GUI.
