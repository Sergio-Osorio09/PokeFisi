# Heurística Avanzada — Evaluación Multidimensional

## ¿Por qué no es suficiente la Heurística Básica?

La Heurística Básica solo mira el HP del Pokémon activo. Ignora:

- ¿Cuántos Pokémon vivos tiene cada jugador?
- ¿El activo tiene ventaja de tipo sobre el rival?
- ¿Quién es más rápido y actúa primero?
- ¿Cómo está el HP promedio del equipo completo?

Un jugador humano considera todo esto simultáneamente. La **Heurística Avanzada** intenta hacer lo mismo usando **4 componentes ponderados**.

---

## La función de evaluación

```
score = w0 × superv  +  w1 × hp_diff  +  w2 × tipo  +  w3 × vel
```

Cada componente es un **diferencial**: mide la diferencia entre tu situación y la del rival. Si es positivo, tienes ventaja en esa dimensión. Si es negativo, el rival te supera ahí.

Los **pesos** `[w0, w1, w2, w3]` controlan cuánto importa cada dimensión.

**Pesos por defecto:**

| Peso | Componente | Valor |
|---|---|---|
| w0 | supervivencia | 0.40 |
| w1 | hp_diff | 0.35 |
| w2 | tipo | 0.15 |
| w3 | velocidad | 0.10 |

---

## Los 4 componentes explicados

### Componente 0 — Supervivencia (`superv`)

```
superv = (Pokémon vivos propios - Pokémon vivos rivales) / total
```

Mide la **ventaja numérica** del equipo. Si tienes 3 Pokémon vivos y el rival 1:

```
superv = (3 - 1) / 3 = +0.67  → gran ventaja
```

Si ambos tienen 2 vivos:

```
superv = (2 - 2) / 3 = 0.00  → equilibrado
```

Este es el componente **más importante** (w0=0.40) porque perder Pokémon es irreversible.

---

### Componente 1 — Diferencial de HP (`hp_diff`)

```
hp_diff = HP_promedio_propio% - HP_promedio_rival%
```

A diferencia de la Heurística Básica, aquí se considera el **equipo completo**, no solo el activo:

```
Mi equipo:     Charizard (80%), Snorlax (100%), Mewtwo (0% — faintado)
Equipo rival:  Pinsir (40%),    Gyarados (75%), Dragonite (90%)

hp_promedio_mío   = (0.80 + 1.00 + 0.00) / 3 = 0.60
hp_promedio_rival = (0.40 + 0.75 + 0.90) / 3 = 0.68

hp_diff = 0.60 - 0.68 = -0.08  → el rival tiene mejor HP promedio
```

Esto captura el **desgaste acumulado** de la batalla, no solo el estado inmediato.

---

### Componente 2 — Ventaja de tipo (`tipo`)

```
tipo = (mejor_mult_mío - mejor_mult_rival) / 4.0
```

`mejor_mult` es el mayor multiplicador de tipo que puede conseguir el Pokémon activo con sus movimientos disponibles.

```
Yo (Charizard) contra Snorlax (tipo Normal):
  Fire Blast → Normal: x1.0
  Air Slash  → Normal: x1.0
  mejor_mult_mío = 1.0

Rival (Snorlax) contra Charizard (tipos Fire/Flying):
  Earthquake → Fire/Flying: x1.0
  Blizzard   → Fire/Flying: x1.0
  mejor_mult_rival = 1.0

tipo = (1.0 - 1.0) / 4.0 = 0.00  → sin ventaja de tipo
```

Otro ejemplo con ventaja clara:

```
Yo (Vaporeon, Water) contra Charizard (Fire/Flying):
  Surf → Fire/Flying: x2.0
  mejor_mult_mío = 2.0

Rival (Charizard) contra Vaporeon (Water):
  Fire Blast → Water: x0.5
  mejor_mult_rival = 0.5

tipo = (2.0 - 0.5) / 4.0 = +0.375  → ventaja de tipo significativa
```

El divisor 4.0 normaliza el rango: el máximo absoluto es x4.0 (doble efectividad doble).

---

### Componente 3 — Ventaja de velocidad (`vel`)

```
vel = (velocidad_propia - velocidad_rival) / MAX_SPEED
```

`MAX_SPEED = 130` (la velocidad máxima del roster: Mewtwo y Jolteon).

```
Yo (Jolteon, SPE=265 en nivel 100) vs rival (Snorlax, SPE=65 en nivel 100):
vel = (265 - 65) / 130 = +1.54  → muy superior en velocidad
```

> Nota: los stats en PokeFisi están calculados a nivel 100 con la fórmula `2×base + 5`, por lo que los valores reales son mayores que los base.

La velocidad importa porque **quien ataca primero puede noquear al rival antes de recibir daño**. Una ventaja de velocidad es una ventaja táctica real.

---

## Cómo se combinan los componentes

```
Ejemplo completo:

superv  = +0.33  (tengo 1 Pokémon más vivo)
hp_diff = +0.18  (mi equipo tiene mejor HP promedio)
tipo    = +0.10  (leve ventaja de tipo)
vel     = -0.07  (el rival es un poco más rápido)

score = 0.40×0.33 + 0.35×0.18 + 0.15×0.10 + 0.10×(-0.07)
      = 0.132     + 0.063     + 0.015     + (-0.007)
      = +0.203
```

Un score de +0.20 indica una ventaja moderada. El score perfecto sería +1.0 (ganas todos los componentes al máximo). El peor sería -1.0.

---

## Paso a paso: cómo decide cada turno

La decisión sigue el mismo patrón greedy que la Básica, pero la función de evaluación es más rica.

### Paso 1 — Para cada acción posible, simular y evaluar

```
Acciones disponibles: [Hyper Beam, Earthquake, Fire Blast, → Snorlax]

Simular Hyper Beam:
  → Rival queda en 20% HP
  superv  = (3-2)/3 = 0.33   (rival faintó)
  hp_diff = 0.60 - 0.20 = +0.40
  tipo    = (1.0 - 1.0)/4 = 0.00
  vel     = (265 - 130)/130 = +1.04  → normalizado a rango sensato: +0.20

  score = 0.40×0.33 + 0.35×0.40 + 0.15×0.00 + 0.10×0.20
        = 0.132 + 0.140 + 0.000 + 0.020
        = +0.292  ← mejor score hasta ahora

Simular Earthquake:
  → Rival queda en 50% HP
  superv  = (3-3)/3 = 0.00  (nadie faintó)
  hp_diff = 0.60 - 0.50 = +0.10
  ...
  score   = +0.08

Simular → Snorlax:
  → Sin daño al rival
  superv  = 0.00
  hp_diff = 0.60 - 0.80 = -0.20  (rival tiene más HP promedio)
  ...
  score   = -0.12
```

### Paso 2 — Elegir el mayor score

```
Hyper Beam:  +0.292  ★ ELEGIDO
Earthquake:  +0.080
Fire Blast:  +0.040
→ Snorlax:   -0.120
```

---

## El panel Cerebro en la GUI

El panel muestra las barras de daño igual que la Básica, pero añade el **desglose de los 4 componentes** del movimiento elegido:

```
J2: Heuristica Avanzada
w0=0.40*superv  w1=0.35*hp  w2=0.15*tipo  w3=0.10*vel
──────────────────────────────────────────────────────────
* Hyper Beam   ████████░░  158HP  rival:20%   +0.29
  Earthquake   ██████░░░░  120HP  rival:50%   +0.08
  Fire Blast   █████░░░░░   95HP  rival:60%   +0.04
  -> Snorlax   ░░░░░░░░░░    0HP  rival:80%   -0.12
──────────────────────────────────────────────────────────
Elegido:  superv:+0.13  hp:+0.14  tipo:+0.00  vel:+0.02
```

El desglose revela **por qué** se eligió esa acción: en este caso, principalmente por supervivencia y HP.

---

## El efecto de los pesos

Los pesos determinan la personalidad estratégica del agente:

| Configuración | Comportamiento |
|---|---|
| w0 alto (supervivencia) | Prioriza no perder Pokémon; juega conservador |
| w1 alto (HP) | Prioriza el desgaste; prefiere golpes consistentes |
| w2 alto (tipo) | Busca ventajas de tipo; cambia para contrarrestar |
| w3 alto (velocidad) | Prefiere Pokémon rápidos; valora atacar primero |

Los pesos por defecto `[0.40, 0.35, 0.15, 0.10]` fueron elegidos a mano. El **Algoritmo Genético** los optimiza automáticamente.

---

## Fortalezas y debilidades

### ✅ Fortalezas
- Considera 4 dimensiones estratégicas simultáneamente
- Mira el equipo completo, no solo el activo
- Usa ventaja de tipo para detectar buenos matchups
- Valora la velocidad como ventaja táctica

### ❌ Debilidades
- Sigue siendo **greedy**: solo mira 1 turno hacia adelante
- No anticipa la respuesta del rival (eso lo hace el Minimax)
- Los pesos por defecto no son óptimos: el Algoritmo Genético los mejora
- Dos movimientos con el mismo score de daño pueden tener tipo diferente — la heurística no lo distingue directamente salvo por el componente `tipo`

---

## Pseudocódigo completo

```
PARA cada acción en acciones_posibles:
    sim = copiar(estado_actual)
    aplicar_acción(sim, acción)

    # Componente 0: supervivencia
    superv = (vivos_propios(sim) - vivos_rivales(sim)) / total

    # Componente 1: HP promedio del equipo
    hp_diff = hp_promedio_propio(sim) - hp_promedio_rival(sim)

    # Componente 2: ventaja de tipo del activo
    tipo = (mejor_mult(mío, rival) - mejor_mult(rival, mío)) / 4.0

    # Componente 3: ventaja de velocidad
    vel = (velocidad_mía - velocidad_rival) / MAX_SPEED

    score = w0×superv + w1×hp_diff + w2×tipo + w3×vel

    SI score > mejor_score:
        mejor_score  = score
        mejor_acción = acción

DEVOLVER mejor_acción
```
