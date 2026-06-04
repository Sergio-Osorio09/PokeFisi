# Minimax con Poda Alfa-Beta — Planificación a Futuro

## ¿Qué es Minimax?

**Minimax** es un algoritmo de toma de decisiones para juegos de dos jugadores. La idea central es:

- **Tú** quieres **maximizar** tu puntuación (nodo MAX)
- **El rival** quiere **minimizar** tu puntuación (nodo MIN)

Ambos juegan de forma óptima. Tú eliges la acción que te da la mejor puntuación asumiendo que el rival hará lo peor posible para ti.

```
Situación actual
      │
   [MAX: yo elijo]
   ╱        ╲
Acción A    Acción B
   │             │
[MIN: rival] [MIN: rival]
 ╱    ╲       ╱    ╲
a1    a2     b1    b2
+5   -2     +3    +8
      ↑ rival elige lo peor para mí
MIN(+5,-2) = -2    MIN(+3,+8) = +3
                              ↑
MAX(-2, +3) = +3  → elegir Acción B
```

El resultado: eligiendo la Acción B, garantizas una puntuación de al menos +3 sin importar lo que haga el rival.

---

## El problema que resuelve en PokeFisi

Las Heurísticas Básica y Avanzada son **greedy**: solo miran 1 turno hacia adelante y no consideran la respuesta del rival. Pueden elegir un movimiento que parece bueno ahora pero que deja al Pokémon vulnerable al siguiente ataque.

Minimax **mira N turnos hacia adelante** y asume que el rival siempre elegirá la peor opción para ti. Esto produce decisiones más robustas aunque requiere más tiempo de cálculo.

---

## Vocabulario fundamental

| Término | Significado en PokeFisi |
|---|---|
| **Profundidad (d)** | Cuántos turnos completos mira hacia adelante |
| **Nodo MAX** | Turno donde yo elijo — maximizo mi puntuación |
| **Nodo MIN** | Turno donde el rival elige — minimiza mi puntuación |
| **Estado terminal** | Batalla terminada (alguien ganó) |
| **Función heurística** | Puntuación del estado cuando no hay más profundidad |
| **Árbol de búsqueda** | El conjunto de todos los estados explorados |
| **Poda alfa-beta** | Técnica para descartar ramas del árbol sin explorarlas |
| **Paranoid** | Asumir que el rival siempre juega de forma óptima contra ti |

---

## La formulación "Paranoid"

Las batallas Pokémon son simultáneas: ambos jugadores eligen su acción al mismo tiempo, sin saber qué hará el rival. Minimax fue diseñado para juegos secuenciales (ajedrez, damas).

La solución es la **formulación paranoid (árbol alternante)**:

1. **Nodo MAX**: yo elijo mi acción para este turno
2. **Nodo MIN**: el rival elige su acción para el mismo turno
3. Cuando ambas acciones están fijadas, se **simula el turno completo** (con prioridad por velocidad) y se desciende al siguiente nivel

```
Profundidad d=2:

Nivel 0 (tú eleges):
  Acción A  Acción B  Acción C
     │          │          │
Nivel 0 (rival elige, dado que tú elegiste A):
  r1  r2  r3   r1  r2  r3   r1  r2  r3
  │   │   │    │   │   │    │   │   │
Simular turno (A+r1), (A+r2), ... → evaluar

Nivel 1 (tú eleges de nuevo):
  ...y así hasta profundidad d=2
```

Cada nivel de profundidad = 1 turno completo de batalla.

---

## Poda Alfa-Beta: cortar lo que no necesitamos explorar

Sin poda, el árbol crece exponencialmente: con 4 movimientos por jugador y profundidad 3, habría `(4×4)^3 = 4.096` estados por explorar.

La **poda alfa-beta** elimina ramas que no pueden afectar la decisión final:

- **α (alfa)**: la mejor puntuación que tú ya garantizas (empieza en -∞)
- **β (beta)**: la mejor puntuación que el rival ya garantiza para él (empieza en +∞)

```
         [MAX]
         α=-∞
        ╱    ╲
     [MIN]   [MIN]
     β=+∞    β=+∞
    ╱   ╲
  +5   ?
  ↑
  α = max(-∞, 5) = 5

Ahora el MIN explora el segundo hijo. Si encuentra -2:
  β = min(+∞, -2) = -2

Si β(-2) ≤ α(5): PODA. El MAX ya tiene mejor opción (5 > -2).
No hace falta explorar más hijos de este MIN.
```

En la práctica, la poda alfa-beta puede reducir el árbol a la **raíz cuadrada** del tamaño original, permitiendo el doble de profundidad en el mismo tiempo.

---

## Paso a paso: cómo decide cada turno (d=2)

### Situación inicial

```
Yo (Minimax): Charizard activo, 3 movimientos disponibles
Rival:        Pinsir activo, 4 movimientos disponibles
Profundidad:  2 turnos
```

### Árbol a explorar (simplificado)

```
Turno actual — yo elijo:

├─ [Fire Blast] → turno actual — rival elige:
│    ├─ [Hyper Beam] → simular turno → nuevo estado → evaluar a profundidad 1
│    ├─ [Earthquake] → simular turno → nuevo estado → evaluar a profundidad 1
│    ├─ [X-Scissor]  → simular turno → nuevo estado → evaluar a profundidad 1
│    └─ [→ Blastoise]→ simular turno → nuevo estado → evaluar a profundidad 1
│       → MIN(puntuaciones) = la peor para mí
│
├─ [Air Slash]  → rival elige → MIN(...)
└─ [Flamethrower]→ rival elige → MIN(...)

MAX(MIN_FireBlast, MIN_AirSlash, MIN_Flamethrower) → acción elegida
```

### Simulación de turno

Cuando se tienen ambas acciones fijadas, se simula el turno completo con prioridad por velocidad:

```
Yo: Fire Blast (SPE Charizard = 205)
Rival: Hyper Beam (SPE Pinsir = 185)

Charizard es más rápido → ataca primero
  → Fire Blast daña a Pinsir: 45 HP de daño
  → Pinsir queda en 195/240 HP

Pinsir contraataca con Hyper Beam
  → Pinsir daña a Charizard: 80 HP de daño
  → Charizard queda en 186/266 HP

Estado resultante → evaluar con función heurística
```

### Evaluación heurística (misma que Avanzada)

```
score = w0×superv + w1×hp_diff + w2×tipo + w3×vel
      = 0.40×(vivos_míos - vivos_rival)/total
      + 0.35×(HP_prom_mío - HP_prom_rival)
      + 0.15×(mejor_tipo_mío - mejor_tipo_rival)/4
      + 0.10×(vel_mía - vel_rival)/130
```

Los estados terminales (victoria/derrota) reciben puntuación extrema:
- Victoria propia: **+1.0**
- Derrota propia: **-1.0**
- Empate: **0.0**

---

## Las profundidades disponibles y su coste

| Profundidad | Turnos mirando | Tiempo aprox. | Calidad |
|---|---|---|---|
| d=2 | 2 turnos | ~10 ms/decisión | Buena |
| d=3 | 3 turnos | ~130 ms/decisión | Muy buena |
| d=4 | 4 turnos | ~1.5 s/decisión | Excelente |

> Tiempos medidos tras optimizar la copia de estado (clon ligero en lugar de `deepcopy`), que aceleró la búsqueda en torno a un orden de magnitud. Varían según la máquina.

Con d=3, la IA "ve" 3 turnos completos hacia adelante: su movimiento, la respuesta del rival, y su siguiente movimiento. Eso le permite evitar trampas obvias y preparar combinaciones de dos turnos.

---

## Ejemplo concreto de por qué Minimax es superior

```
Situación: mi Pokémon tiene poca vida. El rival tiene un movimiento letal.

Heurística Básica:
  Evalúa: "Hyper Beam hace 80 HP de daño al rival → +0.30 score"
  Elige:  Hyper Beam
  Resultado: el rival ataca primero (es más rápido) y me noqueó.

Minimax d=2:
  Nodo MAX (yo elijo Hyper Beam):
    Nodo MIN (rival elige su ataque más fuerte):
      Simulo: rival ataca primero → yo faintado → puntúa -0.6 (mala)

  Nodo MAX (yo elijo cambio → Snorlax):
    Nodo MIN (rival elige su ataque más fuerte):
      Simulo: rival ataca a Snorlax (que tiene mucha vida) → puntúa +0.1

  MAX(-0.6 de Hyper Beam, +0.1 de cambio) → ELEGIR CAMBIO
```

El Minimax descubrió que atacar significaba ser noqueado primero. La Heurística Básica no lo vio porque no mira la respuesta del rival.

---

## El auto-reemplazo en las simulaciones

En PokeFisi, cuando un Pokémon fainta, el jugador envía al siguiente automáticamente. Minimax lo simula dentro del árbol:

```python
def _auto_replace(state, player_id):
    if not state.get_active(player_id).is_alive():
        next_idx = state.next_alive_index(player_id)
        if next_idx >= 0:
            state.set_active_index(player_id, next_idx)
```

Esto se aplica después de cada simulación de turno para mantener la coherencia del estado.

---

## Fortalezas y debilidades

### ✅ Fortalezas
- **Mira el futuro**: detecta trampas y oportunidades que la heurística greedy no ve
- **Robustez**: garantiza el mejor resultado posible asumiendo que el rival juega óptimamente
- **Poda alfa-beta**: hace eficiente la búsqueda sin perder calidad

### ❌ Debilidades
- **Lento con profundidades altas**: d=4 tarda ~1.8 segundos por turno
- **Horizonte limitado**: a d=2 solo ve 2 turnos, puede equivocarse en estrategias de más largo plazo
- **Asumir óptimo del rival**: en la práctica el rival no siempre juega perfecto, lo que puede hacer que Minimax sea demasiado cauteloso
- **Sin memoria**: recalcula desde cero cada turno (no hay tabla de transposición)
- **Sin panel cerebro aún**: el árbol de búsqueda es difícil de visualizar en tiempo real

---

## Pseudocódigo completo

```
FUNCIÓN choose_action(estado, yo):
    mejor_score = -∞
    mejor_acción = ninguna

    PARA cada mi_acción en acciones_posibles(yo):
        score = minimax(estado, profundidad, -∞, +∞, yo, rival, mi_acción)
        SI score > mejor_score:
            mejor_score  = score
            mejor_acción = mi_acción

    DEVOLVER mejor_acción


FUNCIÓN minimax(estado, prof, α, β, yo, rival, mi_acción):

    SI estado es terminal:
        DEVOLVER puntuación_terminal(estado, yo)  # ±1.0

    SI prof == 0:
        DEVOLVER evaluar_heurística(estado, yo)

    SI mi_acción es None:  # NODO MAX: yo elijo
        mejor = -∞
        PARA cada acción en acciones_posibles(yo):
            val = minimax(estado, prof, α, β, yo, rival, acción)
            mejor = max(mejor, val)
            α = max(α, mejor)
            SI β ≤ α: PARAR  # poda β
        DEVOLVER mejor

    SINO:  # NODO MIN: rival elige
        mejor = +∞
        PARA cada acción_rival en acciones_posibles(rival):
            sim = copiar(estado)
            simular_turno(sim, yo, mi_acción, acción_rival)
            val = minimax(sim, prof-1, α, β, yo, rival, None)
            mejor = min(mejor, val)
            β = min(β, mejor)
            SI β ≤ α: PARAR  # poda α
        DEVOLVER mejor
```
