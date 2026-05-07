# Manual Técnico de PokeFisi

## Guía completa del código, la IA y sus decisiones

---

## Tabla de Contenidos

1. [¿Qué es PokeFisi?](#1-qué-es-pokefisi)
2. [Estructura del proyecto](#2-estructura-del-proyecto)
3. [Motor de combate — engine/](#3-motor-de-combate--engine)
   - 3.1 [La clase Pokemon](#31-la-clase-pokemon)
   - 3.2 [La clase Move](#32-la-clase-move)
   - 3.3 [El estado de la batalla — BattleState](#33-el-estado-de-la-batalla--battlestate)
   - 3.4 [La fórmula de daño](#34-la-fórmula-de-daño)
   - 3.5 [Tabla de tipos — TYPE_CHART](#35-tabla-de-tipos--type_chart)
   - 3.6 [El flujo de batalla — Battle](#36-el-flujo-de-batalla--battle)
4. [Inteligencia Artificial — ai/](#4-inteligencia-artificial--ai)
   - 4.1 [Contrato base — Agent](#41-contrato-base--agent)
   - 4.2 [Agente Aleatorio — RandomAgent](#42-agente-aleatorio--randomagent)
   - 4.3 [Heurística Básica — HeuristicBasicAgent](#43-heurística-básica--heuristicbasicagent)
   - 4.4 [Heurística Avanzada — HeuristicAdvancedAgent](#44-heurística-avanzada--heuristicadvancedagent)
   - 4.5 [Los 6 factores de evaluación en detalle](#45-los-6-factores-de-evaluación-en-detalle)
   - 4.6 [Los pesos — qué controlan y cómo cambiarlos](#46-los-pesos--qué-controlan-y-cómo-cambiarlos)
   - 4.7 [Cómo la IA se conecta al juego](#47-cómo-la-ia-se-conecta-al-juego)
5. [Configuración global — config.py](#5-configuración-global--configpy)
6. [Datos — data/](#6-datos--data)
7. [Cómo jugar — Modo GUI](#7-cómo-jugar--modo-gui)
8. [Cómo jugar — Modo Consola](#8-cómo-jugar--modo-consola)
9. [Los 30 Pokémon disponibles](#9-los-30-pokémon-disponibles)
10. [Los movimientos y sus estadísticas](#10-los-movimientos-y-sus-estadísticas)
11. [Ventajas y desventajas de tipo](#11-ventajas-y-desventajas-de-tipo)
12. [Estrategias contra cada IA](#12-estrategias-contra-cada-ia)

---

## 1. ¿Qué es PokeFisi?

PokeFisi es un simulador de combates por turnos inspirado en Pokémon, desarrollado como proyecto académico de Inteligencia Artificial. Dos jugadores —humanos o agentes de IA— se enfrentan con equipos de 3 o 4 Pokémon. El objetivo es derrotar a todos los Pokémon del equipo rival.

El proyecto implementa tres niveles de agentes inteligentes, desde elecciones aleatorias hasta una función heurística compuesta de seis factores con pesos configurables. Comprender cómo estos agentes evalúan el estado del juego y toman decisiones es el núcleo de este manual.

---

## 2. Estructura del proyecto

```
PokeFisi/
├── main.py                  ← punto de entrada (--gui o --console)
├── config.py                ← constantes globales (K, FPS, colores...)
│
├── data/
│   ├── pokemon.json         ← los 30 Pokémon con stats y pool de movimientos
│   └── moves.json           ← todos los movimientos disponibles
│
├── engine/                  ← motor de combate puro (sin GUI ni IA)
│   ├── pokemon.py           ← clase Pokemon
│   ├── move.py              ← clase Move
│   ├── damage.py            ← fórmula de daño + tabla de tipos
│   ├── state.py             ← BattleState (fotografía del juego)
│   ├── battle.py            ← flujo de turnos
│   └── loader.py            ← carga de JSON a objetos Python
│
├── ai/                      ← agentes de IA
│   ├── base_agent.py        ← clase abstracta Agent
│   ├── random_agent.py      ← Agente Aleatorio
│   ├── heuristic_basic.py   ← Heurística Básica
│   └── heuristic_advanced.py← Heurística Avanzada (con pesos)
│
├── gui/                     ← interfaz gráfica (pygame)
│   ├── game_manager.py      ← máquina de estados de la GUI
│   └── screens/             ← pantallas individuales
│
└── console/                 ← interfaz de texto
    ├── console_menu.py      ← menú principal en consola
    ├── console_select.py    ← selección de Pokémon e IA
    └── console_battle.py    ← visualización de la batalla en texto
```

**Principio de diseño clave:** el módulo `engine/` no depende de pygame, consola, ni IA. Funciona con datos puros. Esto significa que cualquier mejora al motor de combate beneficia automáticamente a todos los modos y agentes.

---

## 3. Motor de combate — engine/

### 3.1 La clase Pokemon

**Archivo:** `engine/pokemon.py`

Representa a un Pokémon durante la batalla. Carga sus datos desde el diccionario JSON y selecciona 4 movimientos al azar de su pool al inicio de cada batalla.

```python
class Pokemon:
    def __init__(self, data: dict, available_moves: list):
        self.id          = data["id"]
        self.name        = data["name"]
        self.types       = data["types"]          # lista, ej: ["Dragon", "Flying"]
        self.max_hp      = data["stats"]["hp"]
        self.current_hp  = self.max_hp            # empieza con vida completa
        self.attack      = data["stats"]["attack"]
        self.defense     = data["stats"]["defense"]
        self.speed       = data["stats"]["speed"]
        # Selección aleatoria de 4 movimientos del pool asignado al Pokémon
        self.moves = random.sample(available_moves, min(4, len(available_moves)))
```

**Métodos importantes:**

| Método | Qué hace |
|---|---|
| `is_alive()` | Devuelve `True` si `current_hp > 0` |
| `take_damage(dmg)` | Reduce `current_hp` por `dmg`, mínimo 0 |
| `hp_ratio()` | Devuelve `current_hp / max_hp` (valor entre 0 y 1) |
| `get_available_moves()` | Devuelve la lista de los 4 movimientos activos |

`hp_ratio()` es especialmente importante para la IA: al normalizar el HP en `[0, 1]`, permite comparar Pokémon con HP máximo muy distinto (Snorlax con 160 vs Pikachu con 35) de forma justa.

---

### 3.2 La clase Move

**Archivo:** `engine/move.py`

Representa un movimiento. Sus campos son cargados directamente desde `data/moves.json`:

```python
class Move:
    def __init__(self, data: dict):
        self.id         = data["id"]
        self.name       = data["name"]
        self.type       = data["type"]        # ej: "Fire", "Water"
        self.base_power = data["base_power"]  # poder base (BP)
        self.accuracy   = data["accuracy"]    # precisión en % (100 = nunca falla)
        self.category   = data["category"]    # "physical" o "special"
        self.effect     = data.get("effect", "none")
```

Los campos `category` y `effect` están registrados en los datos pero la versión actual del motor usa la misma fórmula para movimientos físicos y especiales.

---

### 3.3 El estado de la batalla — BattleState

**Archivo:** `engine/state.py`

`BattleState` es la pieza más crítica del sistema. Es una **fotografía completa** del estado del juego en un instante dado: qué Pokémon tiene cada jugador, cuál está activo, cuántos HP les quedan y en qué turno se está.

```python
class BattleState:
    def __init__(self, team1: list, team2: list):
        self.player1_team    = team1   # lista de objetos Pokemon del J1
        self.player2_team    = team2   # lista de objetos Pokemon del J2
        self.active_index_p1 = 0       # índice del Pokémon activo del J1
        self.active_index_p2 = 0       # índice del Pokémon activo del J2
        self.turn_number     = 0       # número de turno actual
```

**Métodos clave:**

| Método | Descripción |
|---|---|
| `get_active(player_id)` | Devuelve el Pokémon activo del jugador dado |
| `get_team(player_id)` | Devuelve la lista completa del equipo |
| `get_active_index(player_id)` | Índice del Pokémon activo |
| `set_active_index(player_id, i)` | Cambia el Pokémon activo |
| `alive_team(player_id)` | Lista solo los Pokémon vivos del equipo |
| `next_alive_index(player_id)` | Primer índice vivo (para reemplazos automáticos) |
| `is_terminal()` | `True` si algún equipo quedó sin Pokémon vivos |
| `get_winner()` | Devuelve 1, 2 o `None` (empate / en curso) |
| `copy()` | **Copia profunda** del estado completo |

#### El método copy() — por qué es fundamental para la IA

```python
def copy(self):
    return copy.deepcopy(self)
```

Este método crea un duplicado completamente independiente del estado. La IA lo usa para **simular acciones sin modificar el estado real de la batalla**. Sin `copy()`, al simular un movimiento se dañaría el estado original y la batalla quedaría corrompida.

El flujo de simulación de la IA es siempre:
```
sim = state.copy()    ← copia independiente
_apply_action(sim)    ← simula sobre la copia
score = _evaluate(sim) ← evalúa la copia
                       ← el estado original queda intacto
```

---

### 3.4 La fórmula de daño

**Archivo:** `engine/damage.py` — función `calculate_damage`

Este es el corazón del motor de combate. Define cuánto daño causa un ataque.

#### La fórmula

```
Damage = max(1,  (Attack / Defense_op) × BasePower  −  Speed_op × K)  ×  type_multiplier
```

| Variable | Descripción |
|---|---|
| `Attack` | Estadística ATK del Pokémon atacante |
| `Defense_op` | Estadística DEF del Pokémon defensor |
| `BasePower` | Poder base del movimiento |
| `Speed_op` | Estadística SPE del Pokémon defensor |
| `K` | Factor de ajuste global, definido en `config.py` como `K = 0.5` |
| `type_multiplier` | Multiplicador de la relación de tipos (0.0 / 0.5 / 1.0 / 2.0 / 4.0) |

#### Análisis de cada término

**Término 1 — `(Attack / Defense_op) × BasePower`:** es el núcleo del daño. Cuanto mayor sea el ATK del atacante y menor el DEF del defensor, más daño. El BP del movimiento amplifica ese cociente. Un atacante con ATK=130 (Machamp) contra un defensor con DEF=40 (Pikachu) produce un cociente de 3.25, que multiplicado por BP=120 da 390 de daño bruto.

**Término 2 — `Speed_op × K`:** la velocidad del defensor resta daño, simulando que un Pokémon rápido esquiva parcialmente el golpe. Con K=0.5, un defensor con SPE=130 (el máximo del roster) reduce 65 puntos de daño. Esta penalización beneficia a los Pokémon lentos pero con alta defensa.

**`max(1, ...)`:** garantiza que el resultado bruto sea al menos 1, evitando daño negativo en casos extremos donde la velocidad es muy alta en relación al daño.

**`max(0, final)`:** tras aplicar el multiplicador de tipo, si hay inmunidad (×0.0), el daño final puede ser 0.

#### Precisión (aleatoriedad)

Antes del cálculo, la función verifica si el movimiento acierta:

```python
if random.randint(1, 100) > move.accuracy:
    return 0, 1.0   # fallo → daño cero
```

Un movimiento con `accuracy = 90` tiene un 10% de probabilidad de fallar. Esta es la única fuente de aleatoriedad en el daño.

#### Implementación completa

```python
# engine/damage.py
def calculate_damage(attacker, move, defender) -> tuple[int, float]:
    # 1. Verificar precisión
    if random.randint(1, 100) > move.accuracy:
        return 0, 1.0          # fallo

    # 2. Daño bruto
    raw = (attacker.attack / max(1, defender.defense)) * move.base_power \
          - defender.speed * K
    raw = max(1, raw)

    # 3. Multiplicador de tipo
    multiplier = get_type_multiplier(move.type, defender.types)
    final = int(raw * multiplier)
    final = max(0, final)      # inmunidad → 0

    return final, multiplier
```

#### Ejemplo concreto

Machamp (ATK=130) usa **Close Combat** (BP=120, Fighting) contra Pikachu (DEF=40, SPE=90, tipo Electric):

```
raw        = (130 / 40) × 120  −  90 × 0.5
           = 3.25 × 120  −  45
           = 390 − 45
           = 345

multiplier = Fighting → Electric → ×1.0  (neutro)

final      = int(345 × 1.0) = 345
```

Pikachu tiene 35 HP. Cae en un golpe.

---

### 3.5 Tabla de tipos — TYPE_CHART

**Archivo:** `engine/damage.py` — diccionario `TYPE_CHART`

Define las relaciones entre tipos atacantes y defensores:

```python
TYPE_CHART = {
    "Fire":  {"Grass": 2.0, "Ice": 2.0, "Bug": 2.0,
               "Water": 0.5, "Fire": 0.5, "Rock": 0.5, "Dragon": 0.5},
    "Water": {"Fire": 2.0, "Ground": 2.0, "Rock": 2.0,
               "Water": 0.5, "Grass": 0.5, "Dragon": 0.5},
    ...
}
```

La función `get_type_multiplier` aplica el multiplicador por cada tipo del defensor (los Pokémon de doble tipo reciben el producto de ambos):

```python
def get_type_multiplier(attack_type: str, defender_types: list[str]) -> float:
    multiplier = 1.0
    chart = TYPE_CHART.get(attack_type, {})
    for def_type in defender_types:
        multiplier *= chart.get(def_type, 1.0)
    return multiplier
```

Un movimiento Hielo contra Dragon/Volador aplica ×2.0 (Dragon) × ×2.0 (Volador) = **×4.0**. Este es el máximo posible en el roster de PokeFisi y es el valor que usa la IA avanzada para normalizar su factor de ventaja de tipo.

---

### 3.6 El flujo de batalla — Battle

**Archivo:** `engine/battle.py`

`Battle` es el director de la partida. Coordina el estado con los dos agentes y ejecuta los turnos.

```python
class Battle:
    def __init__(self, state: BattleState, agent1, agent2):
        self.state  = state
        self.agent1 = agent1
        self.agent2 = agent2
        self.log    = []       # registro de todo lo que ocurrió
```

#### El método step() — un turno completo

```python
def step(self):
    self.state.turn_number += 1

    # Ambos agentes deciden simultáneamente
    action1 = self.agent1.choose_action(self.state, 1)
    action2 = self.agent2.choose_action(self.state, 2)

    # El más veloz actúa primero
    p1, p2 = self.state.active_pokemon_p1, self.state.active_pokemon_p2
    if p1.speed >= p2.speed:
        self._execute_action(1, action1)
        if not self.state.is_terminal():
            self._execute_action(2, action2)
    else:
        self._execute_action(2, action2)
        if not self.state.is_terminal():
            self._execute_action(1, action1)

    # Reemplazar automáticamente a los Pokémon derrotados
    self._auto_replace(1)
    self._auto_replace(2)
```

**Punto clave:** aunque las decisiones se toman "simultáneamente" (ambos `choose_action` se llaman antes de ejecutar cualquier acción), la ejecución es secuencial y ordenada por velocidad. Si el más rápido derrota al oponente, el segundo ya no actúa en ese turno.

#### Ejecución de acciones

```python
def _execute_move(self, player_id, move_index):
    attacker = self.state.get_active(player_id)
    defender = self.state.get_active(3 - player_id)
    move     = attacker.get_available_moves()[move_index]
    damage, mult = calculate_damage(attacker, move, defender)
    defender.take_damage(damage)
    # ... registro en el log

def _execute_switch(self, player_id, pokemon_index):
    self.state.set_active_index(player_id, pokemon_index)
    # ... registro en el log
```

#### Reemplazo automático

```python
def _auto_replace(self, player_id):
    if not self.state.get_active(player_id).is_alive():
        idx = self.state.next_alive_index(player_id)
        if idx >= 0:
            self.state.set_active_index(player_id, idx)
```

Cuando un Pokémon cae, el sistema lo reemplaza automáticamente con el siguiente vivo. Esto ocurre al final de cada turno, no inmediatamente después del golpe de gracia.

---

## 4. Inteligencia Artificial — ai/

### 4.1 Contrato base — Agent

**Archivo:** `ai/base_agent.py`

Todos los agentes heredan de esta clase abstracta. Define el **contrato** que cualquier agente debe cumplir: implementar `choose_action`.

```python
from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, name: str = "Agent"):
        self.name    = name
        self.wins    = 0
        self.battles = 0

    @abstractmethod
    def choose_action(self, state: BattleState, player_id: int) -> dict:
        """
        Recibe el estado completo de la batalla y el ID del jugador (1 o 2).
        Debe devolver:
            {"type": "move",   "move_index": 0-3}
         o  {"type": "switch", "pokemon_index": 0-N}
        """
```

El ID del jugador (1 o 2) es indispensable porque el estado contiene información de ambos jugadores. La IA siempre necesita saber cuál es "ella misma" para evaluar correctamente. La regla es: `opp_id = 3 - player_id`, que convierte 1→2 y 2→1.

#### El método _possible_actions()

Este método de la clase base lista todas las acciones válidas disponibles en un momento dado. Todos los agentes lo usan:

```python
def _possible_actions(self, state: BattleState, player_id: int) -> list[dict]:
    actions = []
    active = state.get_active(player_id)

    # Movimientos disponibles del Pokémon activo
    for i in range(len(active.get_available_moves())):
        actions.append({"type": "move", "move_index": i})

    # Cambios posibles: solo Pokémon vivos que no sean el activo
    for i, p in enumerate(state.get_team(player_id)):
        if p.is_alive() and i != state.get_active_index(player_id):
            actions.append({"type": "switch", "pokemon_index": i})

    # Siempre hay al menos una acción disponible
    return actions if actions else [{"type": "move", "move_index": 0}]
```

En una batalla 3v3 estándar, el número máximo de acciones posibles es 4 (movimientos) + 2 (cambios) = **6 acciones**.

---

### 4.2 Agente Aleatorio — RandomAgent

**Archivo:** `ai/random_agent.py`

El agente más simple. No evalúa nada: elige una acción completamente al azar de entre todas las posibles.

```python
import random

class RandomAgent(Agent):
    def __init__(self):
        super().__init__("Agente Aleatorio")

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        return random.choice(self._possible_actions(state, player_id))
```

**Por qué existe:** es la **línea base de comparación**. Representa el rendimiento de una estrategia sin ninguna inteligencia. Si un agente más avanzado no supera consistentemente al agente aleatorio, su diseño tiene un problema. En teoría, contra oponentes simétricos, el agente aleatorio gana el 50% de las veces.

**Decisiones malas típicas del agente aleatorio:**
- Usar un movimiento de tipo Agua contra un Pokémon de tipo Agua (×0.5, muy ineficiente)
- Cambiar de Pokémon cuando el activo va ganando
- Usar un movimiento de bajo poder cuando hay uno de alto poder disponible del mismo tipo

---

### 4.3 Heurística Básica — HeuristicBasicAgent

**Archivo:** `ai/heuristic_basic.py`

Introduce el concepto central de la IA en PokeFisi: **evaluar el estado del juego con una función heurística** para elegir la mejor acción disponible.

#### La función de evaluación

```python
def _evaluate(self, state: BattleState, player_id: int) -> float:
    me  = state.get_active(player_id)
    opp = state.get_active(3 - player_id)
    return me.hp_ratio() - opp.hp_ratio()
```

La función mide la diferencia de HP normalizado entre el Pokémon propio activo y el oponente:

```
score = (HP_propio / HP_máx_propio)  −  (HP_oponente / HP_máx_oponente)
```

Ambos términos están en `[0, 1]` gracias a `hp_ratio()`. El score resultante está en `[-1, 1]`:

| Score | Situación |
|---|---|
| `+1.0` | Yo tengo HP completo, el oponente tiene 0 HP |
| `0.0` | Ambos tienen el mismo porcentaje de HP |
| `-1.0` | Yo tengo 0 HP, el oponente tiene HP completo |

#### El proceso de decisión

Para cada acción posible, la IA simula qué pasaría y evalúa el resultado:

```python
def choose_action(self, state: BattleState, player_id: int) -> dict:
    best_score  = float("-inf")
    best_action = None

    for action in self._possible_actions(state, player_id):
        sim = state.copy()                           # 1. copia el estado real
        self._apply_action(sim, player_id, action)   # 2. simula la acción
        score = self._evaluate(sim, player_id)        # 3. evalúa el resultado
        if score > best_score:
            best_score  = score
            best_action = action

    return best_action   # 4. devuelve la acción con mayor score
```

Este patrón —copiar, simular, evaluar, elegir el máximo— es el núcleo de **todos** los agentes con heurística del proyecto.

#### La simulación de acciones

```python
def _apply_action(self, state, player_id, action):
    if action["type"] == "switch":
        state.set_active_index(player_id, action["pokemon_index"])
        return
    attacker = state.get_active(player_id)
    defender = state.get_active(3 - player_id)
    moves    = attacker.get_available_moves()
    if action["move_index"] < len(moves):
        dmg, _ = calculate_damage(attacker, moves[action["move_index"]], defender)
        defender.take_damage(dmg)
```

**Nota:** la simulación llama a `calculate_damage`, que incluye el factor de precisión aleatorio. Esto significa que en la misma simulación, un movimiento puede "fallar" por azar. En la práctica, esto rara vez causa decisiones incorrectas porque los movimientos de alta precisión casi nunca fallan, pero es una limitación que la Heurística Avanzada mitiga al calcular el daño esperado.

#### ¿Por qué mejora al agente aleatorio?

Supongamos que el Pokémon activo tiene estos 4 movimientos disponibles:

```
1. Surf        (Water,   BP=95,  Acc=100%)  vs Charizard (Fire/Flying)
2. Ice Beam    (Ice,     BP=90,  Acc=100%)  vs Charizard (Fire/Flying)
3. Body Slam   (Normal,  BP=85,  Acc=100%)
4. Rapid Spin  (Normal,  BP=20,  Acc=100%)
```

El agente aleatorio puede elegir cualquiera con igual probabilidad. La heurística básica simula los cuatro y elige el que más daño cause al defensor, porque más daño → menor HP del oponente → score más alto. En este caso elegiría **Surf** porque Water es superefectivo (×2.0) contra Fire/Flying.

---

### 4.4 Heurística Avanzada — HeuristicAdvancedAgent

**Archivo:** `ai/heuristic_advanced.py`

Es la extensión más completa de la heurística básica. En lugar de evaluar solo el HP del Pokémon activo, considera **seis factores del estado global** del equipo completo, con pesos configurables que determinan la importancia relativa de cada factor.

#### Definición de pesos por defecto

```python
# ai/heuristic_advanced.py
DEFAULT_WEIGHTS = [0.30, 0.25, 0.25, 0.10, 0.05, 0.05]
```

| Índice | Nombre | Valor por defecto |
|---|---|---|
| `w[0]` | `alive_mine` | 0.30 |
| `w[1]` | `hp_avg_mine` | 0.25 |
| `w[2]` | `hp_avg_opp` | 0.25 |
| `w[3]` | `type_adv` | 0.10 |
| `w[4]` | `speed_norm` | 0.05 |
| `w[5]` | `alive_opp` | 0.05 |

La suma de los pesos siempre debe ser 1.0 para que el score total esté en un rango predecible.

#### La función de evaluación completa

```python
def _evaluate(self, state: BattleState, player_id: int) -> float:
    opp_id   = 3 - player_id
    my_team  = state.get_team(player_id)
    opp_team = state.get_team(opp_id)
    total    = len(my_team)

    alive_mine  = sum(1 for p in my_team  if p.is_alive()) / total
    hp_avg_mine = sum(p.hp_ratio() for p in my_team)  / total
    hp_avg_opp  = sum(p.hp_ratio() for p in opp_team) / total

    me  = state.get_active(player_id)
    opp = state.get_active(opp_id)
    type_adv   = self._best_type_advantage(me, opp) / 4.0
    speed_diff = (me.speed - opp.speed) / MAX_SPEED   # en [-1, 1]
    speed_norm = (speed_diff + 1) / 2                  # a [0, 1]
    alive_opp  = sum(1 for p in opp_team if p.is_alive()) / total

    w = self.weights
    return (
          w[0] * alive_mine
        + w[1] * hp_avg_mine
        - w[2] * hp_avg_opp
        + w[3] * type_adv
        + w[4] * speed_norm
        - w[5] * alive_opp
    )
```

---

### 4.5 Los 6 factores de evaluación en detalle

#### Factor 1 — alive_mine (w[0] = 0.30, peso más alto)

```python
alive_mine = sum(1 for p in my_team if p.is_alive()) / total
```

Cuenta cuántos Pokémon propios siguen vivos, normalizado sobre el total del equipo:

- Equipo 3v3 con 3 vivos → `alive_mine = 1.0`
- Equipo 3v3 con 2 vivos → `alive_mine = 0.667`
- Equipo 3v3 con 1 vivo  → `alive_mine = 0.333`

**Por qué tiene el mayor peso (0.30):** conservar Pokémon vivos es el objetivo del juego. Perder un compañero es una desventaja estratégica irreversible —no se puede recuperar HP ni revivir. Este factor penaliza fuertemente las decisiones que sacrifican innecesariamente a un Pokémon.

**Efecto en las decisiones:** la IA evitará dejar al activo en una posición donde caerá en el próximo turno. Si cambiar de Pokémon mantiene `alive_mine` alto (porque el activo tiene muy poco HP), la heurística favorecerá el cambio aunque el sustituto sea ligeramente inferior en combate directo.

---

#### Factor 2 — hp_avg_mine (w[1] = 0.25)

```python
hp_avg_mine = sum(p.hp_ratio() for p in my_team) / total
```

HP promedio de todo el equipo propio, incluyendo los Pokémon derrotados (con `hp_ratio = 0`). Este diseño intencional hace que perder un Pokémon también se refleje en este factor:

- Equipo con 3 Pokémon al 100% HP → `hp_avg_mine = 1.0`
- Equipo con 2 al 100% y 1 derrotado → `hp_avg_mine = 0.667`
- Equipo con todos al 50% → `hp_avg_mine = 0.5`

**Por qué importa:** un equipo con mucho HP tiene más opciones tácticas: puede sobrevivir más turnos, tiene más margen para cambiar Pokémon y recuperar posición. `hp_avg_mine` captura la "salud colectiva" del equipo.

---

#### Factor 3 — hp_avg_opp (w[2] = 0.25, aparece con signo negativo)

```python
hp_avg_opp = sum(p.hp_ratio() for p in opp_team) / total
```

HP promedio del equipo oponente. Aparece **restado** en la función:

```python
- w[2] * hp_avg_opp
```

A menor HP promedio del oponente, mayor el score. La IA maximiza su score atacando al oponente más débil, lo que empuja al agente a concentrar el daño.

**Simetría con Factor 2:** los factores 2 y 3 tienen el mismo peso (0.25). Esto significa que maximizar el HP propio y minimizar el HP oponente tienen la misma importancia. La IA no favorece ser "más defensiva" ni "más ofensiva" por defecto.

---

#### Factor 4 — type_adv (w[3] = 0.10)

```python
type_adv = self._best_type_advantage(me, opp) / 4.0

def _best_type_advantage(self, me, opp) -> float:
    best = 0.0
    for move in me.get_available_moves():
        mult = get_type_multiplier(move.type, opp.types)
        if mult > best:
            best = mult
    return best
```

Mide cuál es el **mejor multiplicador de tipo** disponible entre todos los movimientos del Pokémon activo. El valor se normaliza dividiéndolo por 4.0 (el máximo posible en el roster: doble superefectivo).

| Situación | `type_adv` sin normalizar | `type_adv` normalizado |
|---|---|---|
| Mejor movimiento es inmune al oponente (×0.0) | 0.0 | 0.0 |
| Mejor movimiento es poco efectivo (×0.5) | 0.5 | 0.125 |
| Mejor movimiento es neutro (×1.0) | 1.0 | 0.25 |
| Mejor movimiento es superefectivo (×2.0) | 2.0 | 0.5 |
| Doble superefectivo (×4.0) | 4.0 | 1.0 |

**Por qué tiene un peso menor (0.10):** la ventaja de tipo es importante pero no determina sola el resultado. Un Pokémon con ventaja de tipo pero muy debilitado sigue siendo menos valioso que uno sin ventaja pero con HP completo.

**Efecto en las decisiones:** si la IA tiene a disposición un Pokémon con ventaja de tipo contra el activo del oponente, el factor `type_adv` incentiva cambiarlo al frente, porque hacerlo aumenta el score de ese factor de 0.25 (neutro) a 0.5 (superefectivo), sumando `0.10 × 0.25 = 0.025` al score total.

---

#### Factor 5 — speed_norm (w[4] = 0.05)

```python
speed_diff = (me.speed - opp.speed) / MAX_SPEED   # MAX_SPEED = 130
speed_norm = (speed_diff + 1) / 2                  # normalizado a [0, 1]
```

Mide la diferencia de velocidades entre los dos Pokémon activos, normalizada en `[0, 1]`:

| Situación | `speed_diff` | `speed_norm` |
|---|---|---|
| Yo soy el más rápido del roster (SPE=130), oponente el más lento (SPE=30) | 100/130 ≈ 0.77 | 0.88 |
| Igual velocidad | 0 | 0.50 |
| Yo soy el más lento (SPE=30), oponente el más rápido (SPE=130) | -100/130 ≈ -0.77 | 0.12 |

**Por qué tiene el peso más bajo (0.05):** actuar primero es una ventaja real (puedes eliminar al oponente antes de que ataque), pero es mucho menos determinante que el HP o el número de Pokémon vivos. El peso bajo evita que la IA sacrifique situaciones de ventaja en HP solo por tener algo de ventaja en velocidad.

---

#### Factor 6 — alive_opp (w[5] = 0.05, aparece con signo negativo)

```python
alive_opp = sum(1 for p in opp_team if p.is_alive()) / total
```

Cuenta cuántos Pokémon del oponente siguen vivos. Aparece **restado**:

```python
- w[5] * alive_opp
```

A menos Pokémon vivos del oponente, mayor el score. Complementa al factor 1 desde el lado del oponente.

**Por qué tiene el mismo peso bajo que speed_norm (0.05):** este factor casi duplica la información del factor `hp_avg_opp` (factor 3). Si el HP promedio del oponente es bajo, probablemente tenga Pokémon derrotados. El bajo peso evita contar esa información dos veces con mucha fuerza.

---

### 4.6 Los pesos — qué controlan y cómo cambiarlos

Los pesos son el parámetro más importante de la Heurística Avanzada. Cambiándolos se modifica completamente el estilo de juego del agente sin tocar ningún otro código.

#### Cómo están definidos

```python
# ai/heuristic_advanced.py  (línea 7)
DEFAULT_WEIGHTS = [0.30, 0.25, 0.25, 0.10, 0.05, 0.05]
```

El agente los acepta como parámetro opcional en su constructor:

```python
def __init__(self, weights: list[float] | None = None):
    super().__init__("Heurística Avanzada")
    self.weights = weights if weights is not None else DEFAULT_WEIGHTS[:]
```

Si no se pasan pesos, usa los valores por defecto. Esto significa que puedes instanciar el agente con pesos personalizados sin modificar el archivo:

```python
# Ejemplo: agente muy agresivo que ignora su HP propio
agente = HeuristicAdvancedAgent(weights=[0.10, 0.05, 0.45, 0.25, 0.10, 0.05])
```

#### Cómo modificar los pesos manualmente

**Opción 1 — Editar directamente el archivo (cambio permanente):**

Abre `ai/heuristic_advanced.py` y modifica la línea:

```python
DEFAULT_WEIGHTS = [0.30, 0.25, 0.25, 0.10, 0.05, 0.05]
#                   w0    w1    w2    w3    w4    w5
#                alive_mine hp_mine hp_opp type spd alive_opp
```

**Regla fundamental:** los pesos deben sumar exactamente **1.0**. Si suman más o menos, el score saldrá de su rango esperado y las comparaciones entre acciones perderán coherencia.

```python
# Verificar antes de guardar:
sum([0.30, 0.25, 0.25, 0.10, 0.05, 0.05])  # debe ser 1.0
```

**Opción 2 — Pasar pesos al instanciar (sin modificar el archivo):**

```python
from ai.heuristic_advanced import HeuristicAdvancedAgent

mis_pesos = [0.20, 0.20, 0.30, 0.20, 0.05, 0.05]
agente = HeuristicAdvancedAgent(weights=mis_pesos)
```

#### Efectos de cambiar cada peso

| Si aumentas... | El agente... |
|---|---|
| `w[0]` alive_mine | Se vuelve más **conservador**: evita que sus Pokémon caigan incluso a costa de no atacar |
| `w[1]` hp_avg_mine | Prioriza mantener a todos con HP alto; cambia Pokémon débiles más frecuentemente |
| `w[2]` hp_avg_opp | Se vuelve más **agresivo**: concentra ataques en quien más daño cause |
| `w[3]` type_adv | Cambia de Pokémon más frecuentemente buscando ventaja de tipo |
| `w[4]` speed_norm | Prefiere Pokémon más rápidos; puede cambiar para obtener prioridad de turno |
| `w[5]` alive_opp | Concentra ataques en derrotar Pokémon (no solo bajarles HP) |

#### Ejemplos de configuraciones alternativas

**Agente muy defensivo** (prioriza no perder Pokémon):
```python
[0.45, 0.30, 0.15, 0.05, 0.03, 0.02]
```

**Agente muy ofensivo** (maximiza daño al oponente):
```python
[0.10, 0.05, 0.45, 0.20, 0.10, 0.10]
```

**Agente orientado a ventaja de tipo**:
```python
[0.20, 0.15, 0.20, 0.35, 0.05, 0.05]
```

**Agente equilibrado** (pesos uniformes):
```python
[0.167, 0.167, 0.167, 0.167, 0.166, 0.166]
```

#### La constante MAX_SPEED

```python
# ai/heuristic_advanced.py  (línea 10)
MAX_SPEED = 130
```

Usada para normalizar el factor de velocidad. El valor 130 corresponde a Mewtwo y Jolteon, los Pokémon más rápidos del roster. Si añades un Pokémon con mayor velocidad, actualiza este valor para que la normalización siga siendo correcta.

---

### 4.7 Cómo la IA se conecta al juego

El flujo completo desde que la IA recibe el estado hasta que el juego ejecuta su acción:

```
Battle.step()
    │
    ├─ agent.choose_action(state, player_id)
    │       │
    │       ├─ _possible_actions(state, player_id)
    │       │       → lista de 4-6 acciones posibles
    │       │
    │       └─ Para cada acción:
    │               sim = state.copy()
    │               _apply_action(sim, player_id, action)
    │               score = _evaluate(sim, player_id)
    │               ← mantiene la acción con mayor score
    │
    └─ _execute_action(player_id, best_action)
            │
            ├─ Si "move":   calculate_damage() → take_damage()
            └─ Si "switch": set_active_index()
```

**La IA no modifica nunca el estado real.** Solo trabaja sobre copias (`state.copy()`). El estado real únicamente lo modifica `Battle._execute_action()`, que actúa sobre `self.state` directamente.

**El estado que recibe la IA es completo:** incluye los HP actuales de todos los Pokémon, cuáles están vivos, cuáles son los activos y en qué turno se está. La IA tiene **información perfecta** del estado del juego —no hay información oculta en PokeFisi.

#### Diferencia con un jugador humano

Un humano en modo GUI elige su acción haciendo clic en un botón. El GUI convierte ese clic en el mismo diccionario `{"type": "move", "move_index": i}` y lo pasa a `Battle._execute_action()`. La IA y el humano producen exactamente el mismo formato de salida —el motor de combate no distingue entre ellos.

---

## 5. Configuración global — config.py

Centraliza todas las constantes del proyecto:

```python
# config.py
WINDOW_WIDTH  = 1024   # ancho de la ventana de la GUI (píxeles)
WINDOW_HEIGHT = 768    # alto de la ventana de la GUI (píxeles)
FPS           = 60     # cuadros por segundo de la GUI

K             = 0.5    # factor de velocidad en la fórmula de daño
TEAM_SIZE     = 3      # tamaño de equipo por defecto (no usado directamente en engine)

AI_TURN_DELAY = 1500   # pausa entre turnos en IA vs IA en GUI (milisegundos)
```

**Parámetros que afectan a la IA y el combate:**

- **`K = 0.5`**: aumentarlo hace que la velocidad del defensor reste más daño, favoreciendo a Pokémon lentos con alta defensa. Reducirlo hace que la velocidad importe menos y el daño bruto escale más.
- **`AI_TURN_DELAY`**: no afecta al resultado de la batalla, solo a cuán rápido se puede observar en la GUI.

---

## 6. Datos — data/

### data/pokemon.json

Define los 30 Pokémon. Estructura de cada entrada:

```json
{
  "id": 9,
  "name": "Dragonite",
  "types": ["Dragon", "Flying"],
  "stats": {
    "hp": 91,
    "attack": 134,
    "defense": 95,
    "speed": 80
  },
  "move_ids": [15, 16, 23, 24, 35, 36]
}
```

`move_ids` es el pool de movimientos posibles para este Pokémon. Al inicio de cada batalla se seleccionan 4 al azar entre ellos.

### data/moves.json

Define todos los movimientos disponibles:

```json
{
  "id": 15,
  "name": "Dragon Claw",
  "type": "Dragon",
  "base_power": 80,
  "accuracy": 100,
  "category": "physical",
  "effect": "none"
}
```

Para añadir un movimiento nuevo: agregar una entrada en `moves.json` con un ID único y asignar ese ID en el campo `move_ids` del Pokémon deseado en `pokemon.json`. No hay que tocar ningún archivo Python.

---

## 7. Cómo jugar — Modo GUI

### Paso 1 — Menú Principal

Ejecuta `python3 main.py --gui`. Aparece el menú con el botón **NUEVA BATALLA**.

### Paso 2 — Selección de Modo

Elige entre:
- **HUMANO vs IA**: tú controlas al Jugador 1.
- **IA vs IA**: dos agentes se enfrentan automáticamente para observar.

Luego selecciona el agente de IA (para cada lado en IA vs IA) y el tamaño del equipo (**3 vs 3** o **4 vs 4**).

En el selector de IA puedes ver los pesos de cada agente con barra visual para comparar qué factores prioriza cada uno.

### Paso 3 — Selección de Pokémon

Cuadrícula con los 30 Pokémon. Haz clic para seleccionar (se resalta en verde). Usa la **rueda del ratón** para hacer scroll.

### Paso 4 — La Batalla

- **Zona superior:** campo de batalla con los dos Pokémon activos, sus HP y barras de vida (verde >50%, amarilla >25%, roja <25%).
- **Zona inferior izquierda:** log de batalla con el detalle de cada turno.
- **Zona inferior derecha:** botones de acción (4 movimientos + cambiar Pokémon).

En modo **IA vs IA** los botones están deshabilitados. Los turnos ocurren automáticamente con pausa de 1.5 segundos.

---

## 8. Cómo jugar — Modo Consola

Ejecuta `python3 main.py --console`.

### Menú principal

```
╔══════════════════════════════════════╗
║           POKEFISI  🎮              ║
╠══════════════════════════════════════╣
║  1. Humano vs IA                     ║
║  2. IA vs IA                         ║
║  3. Salir                            ║
╚══════════════════════════════════════╝
```

### Selección de equipo

El juego muestra una tabla con los 30 Pokémon. Escribe los IDs separados por espacios:

```
Elige 3 Pokemon (IDs separados por espacios): 5 9 11
```

### Durante la batalla

Cada turno muestra el estado y las opciones:

```
  1. Flamethrower    (Fire,   Base 90,  Acc 100%)
  2. Dragon Claw     (Dragon, Base 80,  Acc 100%)
  3. Fly             (Flying, Base 90,  Acc  95%)
  4. Hurricane       (Flying, Base 110, Acc  70%)
  5. Cambiar a Blastoise
```

Escribe el número de la acción. El log muestra exactamente qué pasó: movimiento usado, multiplicador de tipo, daño causado y HP restantes.

---

## 9. Los 30 Pokémon disponibles

| # | Pokémon | Tipo | HP | ATK | DEF | SPE |
|---|---|---|---|---|---|---|
| 1 | Pikachu | Electric | 35 | 55 | 40 | 90 |
| 2 | Charizard | Fire/Flying | 78 | 84 | 78 | 100 |
| 3 | Blastoise | Water | 79 | 83 | 100 | 78 |
| 4 | Venusaur | Grass/Poison | 80 | 82 | 83 | 80 |
| 5 | Mewtwo | Psychic | 106 | 110 | 90 | 130 |
| 6 | Gengar | Ghost/Poison | 60 | 65 | 60 | 110 |
| 7 | Machamp | Fighting | 90 | 130 | 80 | 55 |
| 8 | Alakazam | Psychic | 55 | 50 | 45 | 120 |
| 9 | Dragonite | Dragon/Flying | 91 | 134 | 95 | 80 |
| 10 | Lapras | Water/Ice | 130 | 85 | 80 | 60 |
| 11 | Snorlax | Normal | 160 | 110 | 65 | 30 |
| 12 | Arcanine | Fire | 90 | 110 | 80 | 95 |
| 13 | Gyarados | Water/Flying | 95 | 125 | 79 | 81 |
| 14 | Jolteon | Electric | 65 | 65 | 60 | 130 |
| 15 | Vaporeon | Water | 130 | 65 | 60 | 65 |
| 16 | Flareon | Fire | 65 | 130 | 60 | 65 |
| 17 | Rhydon | Ground/Rock | 105 | 130 | 120 | 40 |
| 18 | Exeggutor | Grass/Psychic | 95 | 95 | 85 | 55 |
| 19 | Starmie | Water/Psychic | 60 | 75 | 85 | 115 |
| 20 | Tauros | Normal | 75 | 100 | 95 | 110 |
| 21 | Scyther | Bug/Flying | 70 | 110 | 80 | 105 |
| 22 | Pinsir | Bug | 65 | 125 | 100 | 85 |
| 23 | Electabuzz | Electric | 65 | 83 | 57 | 105 |
| 24 | Magmar | Fire | 65 | 95 | 57 | 93 |
| 25 | Kangaskhan | Normal | 105 | 95 | 80 | 90 |
| 26 | Mr. Mime | Psychic | 40 | 45 | 65 | 90 |
| 27 | Hitmonlee | Fighting | 50 | 120 | 53 | 87 |
| 28 | Hitmonchan | Fighting | 50 | 105 | 79 | 76 |
| 29 | Slowbro | Water/Psychic | 95 | 75 | 110 | 30 |
| 30 | Clefable | Fairy | 95 | 70 | 73 | 60 |

---

## 10. Los movimientos y sus estadísticas

Cada Pokémon tiene asignados entre 5 y 7 movimientos en `data/pokemon.json` (campo `move_ids`). Al inicio de cada batalla se seleccionan **4 de ellos al azar**. Esto añade variabilidad: dos batallas con los mismos Pokémon pueden ser muy distintas.

Los movimientos están definidos en `data/moves.json`:

```json
{
  "id": 1,
  "name": "Flamethrower",
  "type": "Fire",
  "base_power": 90,
  "accuracy": 100,
  "category": "special",
  "effect": "burn_10"
}
```

La Heurística Avanzada analiza **todos los movimientos disponibles** del Pokémon activo para calcular el factor `type_adv`. La aleatoriedad en la selección de movimientos afecta directamente a la calidad de las decisiones de la IA: si le tocan movimientos de tipo desfavorable contra el oponente actual, su `type_adv` será bajo y priorizará otras acciones.

---

## 11. Ventajas y desventajas de tipo

| Resultado | Multiplicador |
|---|---|
| Superefectivo | ×2.0 |
| Normal | ×1.0 |
| Poco efectivo | ×0.5 |
| Inmune | ×0.0 |
| Doble superefectivo | ×4.0 |

### Tabla de relaciones principales

| Tipo atacante | Superefectivo (×2) contra | Poco efectivo (×0.5) contra | Inmune (×0) contra |
|---|---|---|---|
| Fire | Grass, Ice, Bug | Water, Fire, Rock, Dragon | — |
| Water | Fire, Ground, Rock | Water, Grass, Dragon | — |
| Electric | Water, Flying | Electric, Grass, Dragon | Ground |
| Grass | Water, Ground, Rock | Fire, Grass, Poison, Flying, Bug, Dragon | — |
| Psychic | Fighting, Poison | Psychic | Dark |
| Ghost | Ghost, Psychic | — | Normal, Dark |
| Fighting | Normal, Ice, Rock, Dark | Poison, Bug, Psychic, Flying, Fairy | Ghost |
| Dragon | Dragon | Steel | Fairy |
| Ice | Grass, Ground, Flying, Dragon | Water, Ice | — |
| Fairy | Fighting, Dragon, Dark | Fire, Poison, Steel | — |
| Ground | Fire, Electric, Poison, Rock, Steel | Grass, Bug | Flying |
| Rock | Fire, Ice, Flying, Bug | Fighting, Ground, Steel | — |
| Poison | Grass, Fairy | Poison, Ground, Rock, Ghost | Steel |

---

## 12. Estrategias contra cada IA

### Contra el Agente Aleatorio

Cualquier estrategia funciona. Usa siempre el movimiento superefectivo disponible. El agente aleatorio puede elegir acciones subóptimas incluso cuando tiene mejores alternativas.

### Contra la Heurística Básica

La heurística básica solo ve el HP de los dos Pokémon activos y elige siempre el movimiento que más daño inmediato cause. No predice más allá de un turno. Puedes explotarlo:

- **Cambiar preventivamente:** si tu Pokémon activo tiene desventaja de tipo pero uno en el equipo tiene ventaja, la heurística básica no anticipa el cambio. Cambia tú primero.
- **Usar Pokémon lentos con alta DEF:** la fórmula de daño penaliza la velocidad del defensor. Slowbro (DEF=110, SPE=30) recibe mucho menos daño del cálculo inicial que lo que la IA proyecta.
- **Movimientos de alta precisión sobre alto poder:** si la IA usa Hydro Pump (BP=110, Acc=80%) y falla, pierdes un turno. Prefiere movimientos con Acc=100%.

### Contra la Heurística Avanzada

Este agente es más difícil de explotar porque evalúa el equipo completo y la ventaja de tipo:

- **Cambia de Pokémon inesperadamente:** el agente avanzado no simula las posibles respuestas del oponente (solo evalúa un turno hacia adelante). Un cambio estratégico puede sorprenderlo.
- **Equipos con alta sinergia de tipos:** el factor `type_adv` (w=0.10) tiene peso moderado. Si tu equipo tiene múltiples tipos que cubren al oponente, el agente necesitará cambiar frecuentemente y eso consume turnos.
- **Ataques con alta precisión y Acc=100:** la simulación de la heurística usa `calculate_damage` que incluye azar. Un agente con movimientos de Acc=100% toma decisiones más predecibles y consistentes que uno con movimientos de baja precisión.

### Cómo modificar la IA para que sea más difícil

Edita `ai/heuristic_advanced.py` y cambia `DEFAULT_WEIGHTS`. Un agente más desafiante para el jugador humano promedio:

```python
# Más agresivo: prioriza destruir al oponente
DEFAULT_WEIGHTS = [0.15, 0.10, 0.40, 0.20, 0.10, 0.05]
```

Recuerda que los pesos siempre deben sumar 1.0.

---

*Manual Técnico de PokeFisi — Proyecto académico de Inteligencia Artificial*
