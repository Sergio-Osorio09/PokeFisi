# Heurística Mejorada — 6 Componentes con KO-Threat y Cobertura de Equipo

## ¿Qué es la Heurística Mejorada?

La **Heurística Mejorada** combina las mejores ideas de la Heurística Avanzada y añade dos nuevos componentes críticos que las versiones anteriores ignoraban:

1. **KO-Threat** — ¿puedo noquear al rival en este turno?
2. **KO-Danger** — ¿puede el rival noquearme a mí?
3. **Cobertura de equipo** — ¿cuántos de mis Pokémon tienen ventaja de tipo sobre el equipo rival?

El resultado es una heurística de **6 componentes con pesos entrenables** que evalúa la situación desde más ángulos que cualquier versión anterior.

---

## La fórmula

```
score = w0×superv  +  w1×hp_pond  +  w2×ko_threat
      + w3×ko_danger  +  w4×cobertura  +  w5×vel
```

Pesos por defecto (suman 1.0):

| Componente  | Peso | Rango |
|-------------|------|-------|
| superv      | 0.25 | [-1, 1] |
| hp_pond     | 0.20 | [-1, 1] |
| ko_threat   | 0.20 | [0, 1]  |
| ko_danger   | 0.15 | [-1, 0] |
| cobertura   | 0.10 | [-1, 1] |
| vel         | 0.10 | [-1, 1] |

---

## Los 6 componentes explicados

### w0 — Supervivencia (`superv`)

Diferencial de Pokémon vivos entre ambos equipos:

```
superv = (mis_vivos - vivos_rival) / total_pokemon
```

- Si tengo 3 vivos y el rival 1: `superv = (3-1)/3 = +0.67`
- Si tengo 1 vivo y el rival 3: `superv = (1-3)/3 = -0.67`

**Rango:** [-1, 1]

---

### w1 — HP Ponderado (`hp_pond`)

Combina el HP del Pokémon activo (peso mayor) con el HP promedio del equipo (peso menor):

```
hp_pond = 0.7 × (HP_activo_mío - HP_activo_rival)
        + 0.3 × (HP_prom_equipo_mío - HP_prom_equipo_rival)
```

Donde `HP_activo = pokemon.current_hp / pokemon.max_hp`.

**Por qué 70/30:** El activo es lo que importa ahora mismo; el equipo importa para el largo plazo.

**Rango:** [-1, 1]

---

### w2 — KO Threat (`ko_threat`) ← NUEVO

Mide qué fracción del HP rival puede quitarle el mejor movimiento disponible:

```
max_daño_mío = max(daño_simulado(yo, mv, rival) para mv en mis_movimientos)
ko_threat    = min(1.0, max_daño_mío / HP_actual_rival)
```

- Si puedo quitar **todo** el HP del rival en un turno: `ko_threat = 1.0`
- Si puedo quitar la **mitad**: `ko_threat = 0.5`
- Si mis movimientos hacen muy poco daño: `ko_threat ≈ 0.0`

**Intuición:** Este componente empuja a la IA a elegir el movimiento de mayor daño cuando tiene al rival en rojo. Una heurística sin KO-threat puede "desperdiciar" el turno con un movimiento débil cuando tenía el KO servido.

**Rango:** [0, 1]

---

### w3 — KO Danger (`ko_danger`) ← NUEVO

Mide el peligro que representa el rival, con descuento si somos más rápidos:

```
max_daño_rival = max(daño_simulado(rival, mv, yo) para mv en sus_movimientos)
raw_danger     = min(1.0, max_daño_rival / HP_actual_mío)
factor_velocidad = 0.5 si yo soy más rápido else 1.0
ko_danger      = -raw_danger × factor_velocidad
```

- Si el rival puede noquearme y es más rápido: `ko_danger = -1.0` (máximo peligro)
- Si el rival puede noquearme pero yo soy más rápido: `ko_danger = -0.5` (puedo atacar antes)
- Si el rival apenas puede rascarme: `ko_danger ≈ 0.0`

**Por qué el factor velocidad:** Si soy más rápido, ataco primero. Si el rival solo puede noquearme **después** de que yo ataque, el peligro real es menor.

**Rango:** [-1, 0]

---

### w4 — Cobertura de Equipo (`cobertura`)

Evalúa qué tan bien cubre mi equipo completo al equipo rival (y viceversa):

```
cobertura = _cov(mis_vivos, rivales_vivos) - _cov(rivales_vivos, mis_vivos)

_cov(atacantes, defensores) =
    promedio sobre cada atacante de:
        max multiplicador_tipo(mv, defensor) para mv en movimientos, defensor en defensores
    dividido entre 4  (normalización: el máximo multiplicador posible es 4×)
```

- Si mis Pokémon tienen al menos un movimiento efectivo (2×) contra todos los rivales: alta cobertura
- Si el rival tiene superefectivos contra todos los míos: cobertura negativa

**Por qué es importante:** Dos equipos con el mismo HP pueden tener situaciones muy distintas dependiendo de los tipos. Un equipo de Pokémon Agua/Tierra/Planta tiene cobertura mutua y ventaja contra equipos de Fuego/Roca.

**Rango:** [-1, 1]

---

### w5 — Velocidad (`vel`)

Diferencial de velocidad del Pokémon activo:

```
vel = (mi_velocidad - velocidad_rival) / MAX_SPEED
```

Donde `MAX_SPEED = 130` (velocidad máxima del set de Pokémon disponibles).

**Rango:** [-1, 1]

---

## Comparación con heurísticas anteriores

| Componente          | Básica | Avanzada | Mejorada |
|---------------------|--------|----------|----------|
| Supervivencia       | ✗      | ✓        | ✓        |
| HP diferencial      | ✓      | ✓        | ✓ (pond.)|
| Ventaja de tipo     | ✗      | ✓        | ✓ (cob.) |
| Velocidad           | ✗      | ✓        | ✓        |
| KO Threat           | ✗      | ✗        | ✓        |
| KO Danger           | ✗      | ✗        | ✓        |
| Pesos entrenables   | ✗      | ✓        | ✓        |

---

## Por qué KO-Threat y KO-Danger son el salto clave

### Sin KO-Threat (Heurística Avanzada)

```
Situación: rival tiene 30 HP. Tengo Flamethrower (100 de daño) y Quick Attack (40 de daño).

Avanzada evalúa:
  Flamethrower: score = 0.35×(HP_diff grande) + 0.15×(tipo) + ...  → score = 0.42
  Quick Attack: score = 0.35×(HP_diff pequeño) + 0.15×(tipo) + ... → score = 0.38

→ Elige Flamethrower correctamente, pero solo por suerte de los pesos generales.
```

### Con KO-Threat (Heurística Mejorada)

```
ko_threat con Flamethrower = min(1.0, 100/30) = 1.0  ← ¡KO garantizado!
ko_threat con Quick Attack  = min(1.0, 40/30)  = 1.0  ← también KO (ambos son suficientes)

→ La IA sabe explícitamente que puede noquear, y su score sube en consecuencia.
```

### Sin KO-Danger (Heurística Avanzada)

```
Situación: yo tengo 20 HP. El rival tiene Earthquake (daño simulado = 150).
El rival es más rápido.

Avanzada: evalúa el score del estado pero no detecta explícitamente que morirá este turno.
→ Puede elegir atacar en vez de cambiar, porque el daño que yo hago parece bueno.
```

### Con KO-Danger (Heurística Mejorada)

```
ko_danger = -min(1.0, 150/20) × 1.0 = -1.0  ← peligro máximo (rival es más rápido)

→ El componente KO-Danger penaliza fuertemente quedarse.
→ La IA considera cambiar a un Pokémon más resistente.
```

---

## Los pesos entrenables

Los 6 pesos se optimizan con el mismo **Hill-Climbing** que usa la Heurística Avanzada:

```
Inicio:   [0.25, 0.20, 0.20, 0.15, 0.10, 0.10]
          sv    hp    ko+   ko-   cob   vel
```

En cada batalla de entrenamiento:
1. Se perturban los pesos con ruido gaussiano de temperatura decreciente
2. Se normalizan para que sumen 1.0
3. Se juega una batalla contra Agente Aleatorio (50%) o Heurística Básica (50%)
4. Si se gana, se adoptan los nuevos pesos

Los pesos entrenados se guardan en `data/weights_improved_N.json`.

---

## Paso a paso: decisión de un turno

```
Situación: Charizard activo (90/266 HP, SPE=205) vs Pinsir (30/240 HP, SPE=185)

Mis movimientos disponibles:
  1. Flamethrower (tipo Fuego, BP=95)
  2. Air Slash    (tipo Volador, BP=75)
  3. Scratch      (tipo Normal, BP=40)

Componentes para Flamethrower:
  superv   = (3-2)/3 = 0.33  → w0×0.33 = 0.083
  hp_pond  = 0.7×(90/266 - 30/240) + 0.3×(...) ≈ 0.7×(0.24) + ... ≈ +0.17  → w1×0.17 = 0.034
  ko_threat= min(1.0, 140/30) = 1.0  → w2×1.0 = 0.200  ← ¡KO disponible!
  ko_danger= -min(1.0, 60/90) × 0.5 = -0.33  → w3×(-0.33) = -0.050  (soy más rápido)
  cobertura= _cov_diff ≈ +0.3  → w4×0.3 = 0.030
  vel      = (205-185)/130 = 0.15  → w5×0.15 = 0.015

  score(Flamethrower) ≈ 0.083+0.034+0.200-0.050+0.030+0.015 = +0.312

Score de Air Slash y Scratch serán menores porque su ko_threat < 1.0.

→ Elige Flamethrower → Pinsir noqueado.
```

---

## Cómo entrenar desde la consola

```
POKEFISI - Consola
  4. Entrenar Heuristica Mejorada
```

Se pide el número de batallas (mínimo 10). Los pesos resultantes quedan disponibles automáticamente en el selector de IAs de la GUI con el nombre `H.Mejorada-N`.

### Ejemplo de salida

```
=== Entrenar Heuristica Mejorada ===
¿Cuantas batallas para entrenar? (min. 10): 100

  Entrenando 100 batallas vs Random (50%) y HeuristicBasica (50%)...

  [ 10%] Batalla  10/100  |  Win-rate: 62.0%  |  Temp: 0.0957
  [ 20%] Batalla  20/100  |  Win-rate: 65.0%  |  Temp: 0.0764
  ...
  [100%] Batalla 100/100  |  Win-rate: 71.0%  |  Temp: 0.0126

  Entrenamiento completado!
  Guardado en:  data/weights_improved_100.json
  Win-rate:     71.0%

  Pesos aprendidos:
    superv.       0.2712  (base 0.250,  +0.0212)
    hp_pond.      0.1834  (base 0.200,  -0.0166)
    ko_threat     0.2341  (base 0.200,  +0.0341)
    ko_danger     0.1523  (base 0.150,  +0.0023)
    cobertura     0.0908  (base 0.100,  -0.0092)
    velocidad     0.0682  (base 0.100,  -0.0318)
```

---

## Fortalezas y debilidades

### ✅ Fortalezas
- **Detecta KOs**: sabe cuándo puede noquear al rival y lo prioriza
- **Detecta peligro**: sabe cuándo está en peligro de ser noqueado y ajusta su decisión
- **Cobertura de equipo**: valora tener un equipo bien balanceado en tipos
- **HP ponderado**: mezcla la situación inmediata con la del equipo completo
- **Pesos entrenables**: puede mejorar jugando contra rivales reales

### ❌ Debilidades
- **Greedy**: sigue mirando solo 1 turno hacia adelante (no anticipa respuestas futuras como Minimax)
- **Sin memoria**: no recuerda el historial de la batalla
- **Cobertura costosa**: recalcular la cobertura de equipo es más lento que las heurísticas simples
- **Movimientos de estado**: no considera movimientos sin daño (buffs, debuffs) en los componentes KO

---

## Diferencias con las otras heurísticas

| Característica          | Básica | Avanzada | Mejorada | Minimax d=2 |
|-------------------------|--------|----------|----------|-------------|
| Mira turnos futuros     | 1      | 1        | 1        | 2+          |
| Componentes             | 1      | 4        | 6        | 4 (heur.)   |
| KO awareness            | ✗      | ✗        | ✓        | ✓ (implíc.) |
| Pesos entrenables       | ✗      | ✓        | ✓        | ✗           |
| Tiempo por turno        | ~1 ms  | ~2 ms    | ~4 ms    | ~50-280 ms  |
