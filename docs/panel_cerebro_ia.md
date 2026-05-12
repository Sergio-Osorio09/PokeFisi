# Panel Cerebro IA — Visualización del Pensamiento en Tiempo Real

## ¿Qué es el Panel Cerebro?

Durante una batalla en modo **IA vs IA**, la pantalla muestra dos paneles en la columna derecha que revelan en tiempo real **cómo razona cada agente** antes de elegir su acción.

Cada turno, la IA evalúa todas sus opciones (movimientos + cambios de Pokémon), calcula un score para cada una y elige la mejor. El panel hace visible ese proceso que normalmente ocurre de forma invisible.

---

## Layout de los paneles

```
┌─────────────────────────────────┐  ← Campo de batalla (izquierda)
│  Sprites, info HP, log...       │
└─────────────────────────────────┘

┌──────────────────────────────────────────┐  ← BRAIN_X = 548
│  J2: <Nombre agente>                     │  Panel P2 (arriba)
│  <fórmula>                               │
│  ─────────────────────────────────────   │
│  * Movimiento A  ████████░░  42HP  +0.48 │
│    Movimiento B  ██████░░░░  30HP  +0.31 │
│    -> Switch     ░░░░░░░░░░   0HP  -0.05 │
│  ─────────────────────────────────────   │
│  Elegido: superv:+0.33  hp:+0.18  ...   │  (solo Avanzada)
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  J1: <Nombre agente>                     │  Panel P1 (abajo)
│  ...                                     │
└──────────────────────────────────────────┘
```

---

## Elementos del panel

| Elemento | Descripción |
|---|---|
| **Cabecera** | Jugador y nombre del agente |
| **Fórmula** | La ecuación de evaluación que usa ese agente |
| **Filas de acción** | Una fila por cada movimiento o cambio evaluado |
| **Barra roja** | Proporcional al daño estimado que causaría ese movimiento |
| **HP texto** | Daño en HP y porcentaje de HP que le quedaría al rival |
| **Score** | Valor numérico calculado por la heurística (verde = bueno, rojo = malo) |
| **★ / \*** | Marca la acción elegida (fila resaltada en azul) |
| **Desglose** | Solo en Avanzada: contribución de cada componente al score elegido |

---

## Heurística Básica

**Fórmula mostrada:**
```
score = HP_propio% - HP_rival%
```

El agente simula cada acción y evalúa cuánta diferencia de HP queda a su favor. Elige el movimiento que maximize esa diferencia.

**Qué ver en el panel:**
- La barra más larga → más daño al rival → mayor score
- Si elige un cambio (score alto) significa que el rival tiene mucha más vida y conviene preservar el Pokémon actual

**Ejemplo:**
```
J1: Heuristica Basica
score = HP_propio% - HP_rival%
────────────────────────────────────────────
* Hurricane    ████████░░  76HP  rival:0%   +0.68
  Future Sight ████████░░  76HP  rival:0%   +0.68
  Psyshock     ████░░░░░░  44HP  rival:13%  +0.55
  -> Dragonite ░░░░░░░░░░   0HP  rival:32%  +0.00
```

---

## Heurística Avanzada

**Fórmula mostrada:**
```
score = w0*superv + w1*hp + w2*tipo + w3*vel
```

Evalúa 4 diferenciales ponderados por sus pesos. El desglose al pie del panel muestra cuánto aportó cada componente al score del movimiento elegido.

**Los 4 componentes:**

| Componente | Qué mide | Rango |
|---|---|---|
| `superv` | Diferencia de Pokémon vivos | [-1, 1] |
| `hp` | Diferencia de HP promedio del equipo | [-1, 1] |
| `tipo` | Ventaja de tipo del activo | [-1, 1] |
| `vel` | Ventaja de velocidad (actúa primero) | [-1, 1] |

**Qué ver en el panel:**
- Un componente negativo (rojo) indica desventaja en esa dimensión
- La suma de los 4 componentes = score total
- Si `tipo` tiene mucho peso en el movimiento elegido, la IA está priorizando la ventaja de tipo

**Ejemplo:**
```
J2: Heuristica Avanzada
w0=0.40*superv  w1=0.35*hp  w2=0.15*tipo  w3=0.10*vel
────────────────────────────────────────────────────
* Hyper Beam   ████████░░  42HP  rival:0%   -0.13
  Bug Buzz     ████████░░  42HP  rival:0%   -0.13
  Signal Beam  ████████░░  42HP  rival:0%   -0.13
  Earthquake   ████████░░  42HP  rival:0%   -0.13
────────────────────────────────────────────────────
Elegido: superv:+0.00  hp:-0.06  tipo:+0.00  vel:-0.07
```

> En este ejemplo todos los scores son iguales (-0.13) porque el rival ya tiene 0 HP. Los componentes negativos revelan que la IA está en desventaja de HP y velocidad.

---

## Función de pausa (solo IA vs IA)

En modo IA vs IA aparece un botón **PAUSAR** en la esquina inferior derecha.

| Control | Acción |
|---|---|
| Botón **PAUSAR** | Congela la batalla |
| Botón **REANUDAR** | Continúa la batalla |
| Tecla **ESPACIO** | Alterna entre pausar y reanudar |

Cuando la batalla está pausada:
- Los paneles cerebro quedan congelados mostrando la última decisión tomada
- Aparece un indicador **⏸ PAUSADO** en pantalla
- El botón cambia a rojo y su texto a **REANUDAR**

Esto permite leer con calma el razonamiento de ambas IAs, comparar scores y entender por qué cada una eligió su acción.

---

## Implementación técnica

### Cómo el agente expone sus datos

Cada agente que soporta el panel cerebro almacena `last_brain_data` tras cada `choose_action`:

```python
self.last_brain_data = {
    "formula":     "score = HP_propio% - HP_rival%",
    "evaluations": [
        {
            "name":         "Hyper Beam",
            "damage":       76,
            "opp_hp_after": 0,
            "opp_max_hp":   240,
            "score":        0.68,
            "chosen":       True,
            # solo Avanzada:
            "components":   {"superv": 0.0, "hp": 0.18, "tipo": 0.08, "vel": 0.03},
        },
        ...
    ],
}
```

### Cómo la GUI lo consume

`BattleScreen._draw_brain_panel()` lee `agent.last_brain_data` cada frame. Si es `None` (antes del primer turno), muestra "Esperando primer turno...".

### Agentes compatibles

| Agente | Panel cerebro |
|---|---|
| Heurística Básica | Sí — fórmula + barras |
| Heurística Avanzada | Sí — fórmula + barras + desglose de componentes |
| Minimax | No (aún) |
| Genético | Hereda Avanzada — Sí |
| Aleatorio | No |
