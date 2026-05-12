# Heurística Básica — La Primera Estrategia Real

## ¿Qué es una Heurística?

Una **heurística** es una función que le asigna un número a una situación del juego. Ese número representa "qué tan buena es esta situación para mí". Cuanto mayor el número, mejor.

No calcula la jugada perfecta — eso sería imposible en la mayoría de los juegos. En cambio, hace una estimación razonablemente buena en poco tiempo.

> La palabra "heurística" viene del griego *heuriskein*: "descubrir". La IA descubre si una situación es buena o mala sin analizarla exhaustivamente.

---

## El problema que resuelve en PokeFisi

La Heurística Básica responde una pregunta simple: **¿qué movimiento me deja en la mejor situación de HP comparado con el rival?**

Su fórmula de evaluación:

```
score = HP_propio% - HP_rival%
```

Donde `HP%` es el porcentaje de vida actual sobre la vida máxima. Un score positivo significa que tú tienes más vida que el rival. Uno negativo, que el rival tiene ventaja.

---

## Vocabulario clave

| Término | Significado en PokeFisi |
|---|---|
| **Estado** | La situación actual de la batalla (HP, quién está activo, etc.) |
| **Acción** | Un movimiento o un cambio de Pokémon |
| **Simulación** | Aplicar una acción a una copia del estado para ver qué pasaría |
| **Score / Puntuación** | El número que devuelve la función heurística |
| **Greedy (voraz)** | Estrategia que siempre elige la mejor opción inmediata |

---

## Paso a paso: cómo decide cada turno

### Paso 1 — Listar todas las acciones posibles

```
Pokémon activo: Dragonite (138/292 HP)
Rival activo:   Pinsir    (240/240 HP)

Acciones posibles:
  A. Movimiento: Hyper Beam
  B. Movimiento: Earthquake
  C. Movimiento: Fire Blast
  D. Cambio: → Snorlax
```

### Paso 2 — Simular cada acción

Para cada acción, la IA crea una **copia** del estado de la batalla, aplica la acción y observa el resultado.

```
Simular A (Hyper Beam):
  Daño estimado a Pinsir: 158 HP
  → Pinsir queda con 82/240 HP  (34%)
  → Dragonite sigue en 138/292 HP (47%)
  score_A = 0.47 - 0.34 = +0.13

Simular B (Earthquake):
  Daño estimado a Pinsir: 120 HP
  → Pinsir queda con 120/240 HP (50%)
  → Dragonite sigue en 138/292 HP (47%)
  score_B = 0.47 - 0.50 = -0.03

Simular C (Fire Blast):
  Daño estimado a Pinsir: 95 HP
  → Pinsir queda con 145/240 HP (60%)
  → Dragonite sigue en 138/292 HP (47%)
  score_C = 0.47 - 0.60 = -0.13

Simular D (Cambio → Snorlax):
  Snorlax entra activo (no hay daño al rival)
  → Pinsir sigue en 240/240 HP (100%)
  → Snorlax tiene 430/430 HP (100%)
  score_D = 1.00 - 1.00 = 0.00
```

### Paso 3 — Elegir la acción con mayor score

```
score_A = +0.13  ← GANADOR
score_B = -0.03
score_C = -0.13
score_D =  0.00

Acción elegida: Hyper Beam
```

Siempre elige el score más alto. Esto se llama estrategia **greedy** (voraz): toma la mejor ganancia inmediata sin mirar qué pasa después.

---

## Por qué solo mira 1 turno hacia adelante

La Heurística Básica no simula la respuesta del rival. Solo ve **"si yo hago esto, ¿cómo quedo yo?"** y no **"¿qué hará el rival después?"**.

Esto la hace rápida pero limitada:

```
Situación: Pinsir tiene 10 HP y usará un movimiento letal el próximo turno.
Heurística Básica: "Hyper Beam hace más daño → elijo Hyper Beam"
Minimax:           "Si uso Hyper Beam, el rival me noqueará primero por
                    velocidad. Mejor cambiar a alguien más rápido."
```

La Heurística Básica no ve el segundo paso. El Minimax sí.

---

## El daño estimado (simulación determinista)

Para que la simulación sea justa y reproducible, el daño no se calcula con aleatoriedad. Se usa la **fórmula determinista**:

```
daño = (ATK_propio / DEF_rival) × BP_movimiento × mult_tipo × acc/100 - VEL_rival × K
```

Donde:
- `BP` = Base Power del movimiento
- `mult_tipo` = multiplicador de tipo (x0.5, x1.0, x2.0, x4.0)
- `acc` = precisión del movimiento (en %)
- `K` = constante de balanceo (0.25)

Se resta `VEL_rival × K` para penalizar a los rivales rápidos: un Pokémon lento que ataca primero pierde parte de su ventaja.

---

## El panel Cerebro en la GUI

Durante batallas IA vs IA, el panel derecho muestra la evaluación de la Heurística Básica en tiempo real:

```
J1: Heuristica Basica
score = HP_propio% - HP_rival%
────────────────────────────────────────────────────
* Hyper Beam   ████████░░   158HP  rival:34%   +0.13
  Earthquake   ██████░░░░   120HP  rival:50%   -0.03
  Fire Blast   █████░░░░░    95HP  rival:60%   -0.13
  -> Snorlax   ░░░░░░░░░░     0HP  rival:100%  +0.00
```

- La **barra roja** es proporcional al daño que causaría ese movimiento
- `rival:%` muestra cuánta vida le quedaría al rival
- El **score** es el valor calculado por la fórmula
- El movimiento marcado con `*` es el elegido (fila resaltada)

---

## Fortalezas y debilidades

### ✅ Fortalezas
- Siempre elige el movimiento que más daño hace (en proporción)
- Considera la opción de cambiar si el score del cambio supera al de atacar
- Es extremadamente rápida — evalúa todo en microsegundos

### ❌ Debilidades
- **No usa ventaja de tipo**: no sabe que Water es fuerte contra Fire
- **No mira el futuro**: no anticipa el ataque del rival ni sus cambios
- **No cuida la supervivencia del equipo**: solo mira al Pokémon activo
- **Puede cambiar innecesariamente**: si el rival tiene vida llena, el cambio tiene score 0 y puede competir con un ataque débil

---

## Comparación de scores en la práctica

```
Escenario: yo tengo 50% HP, rival tiene 80% HP
→ score inicial = 0.50 - 0.80 = -0.30  (estoy perdiendo)

Si uso el mejor movimiento y dejo al rival en 20% HP:
→ score final = 0.50 - 0.20 = +0.30  (paso a ganar)

Si solo hago 10% de daño y el rival queda en 70%:
→ score final = 0.50 - 0.70 = -0.20  (sigo perdiendo)

La IA elige la primera opción porque +0.30 > -0.20.
```

Este razonamiento es correcto en la mayoría de casos, pero ignora que el rival podría noquearme antes de que yo pueda actuar.

---

## Pseudocódigo

```
PARA cada acción en acciones_posibles:
    estado_simulado = copiar(estado_actual)
    aplicar_acción(estado_simulado, acción)
    
    mi_hp   = estado_simulado.activo_mio.hp_ratio()
    opp_hp  = estado_simulado.activo_rival.hp_ratio()
    score   = mi_hp - opp_hp

    SI score > mejor_score:
        mejor_score  = score
        mejor_acción = acción

DEVOLVER mejor_acción
```
