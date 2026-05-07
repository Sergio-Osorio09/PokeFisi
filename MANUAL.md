# Manual de PokeFisi

## Guía completa del juego, la IA y el código

---

## Tabla de Contenidos

1. [¿Qué es PokeFisi?](#1-qué-es-pokefisi)
2. [Conceptos básicos para nuevos jugadores](#2-conceptos-básicos-para-nuevos-jugadores)
3. [Cómo jugar — Modo GUI](#3-cómo-jugar--modo-gui)
4. [Cómo jugar — Modo Consola](#4-cómo-jugar--modo-consola)
5. [Los 30 Pokémon disponibles](#5-los-30-pokémon-disponibles)
6. [Los movimientos y sus estadísticas](#6-los-movimientos-y-sus-estadísticas)
7. [La fórmula de daño](#7-la-fórmula-de-daño)
8. [Ventajas y desventajas de tipo](#8-ventajas-y-desventajas-de-tipo)
9. [Inteligencia Artificial — Los Agentes](#9-inteligencia-artificial--los-agentes)
10. [Entrenamiento de la IA — Stochastic Hill-Climbing](#10-entrenamiento-de-la-ia--stochastic-hill-climbing)
11. [Arquitectura del código](#11-arquitectura-del-código)
12. [Flujo completo de una batalla](#12-flujo-completo-de-una-batalla)
13. [Estrategias recomendadas](#13-estrategias-recomendadas)

---

## 1. ¿Qué es PokeFisi?

PokeFisi es un simulador de combates por turnos inspirado en Pokémon. Dos jugadores (humanos o agentes de Inteligencia Artificial) se enfrentan con equipos de 3 o 4 Pokémon. El objetivo es derrotar a todos los Pokémon del equipo rival.

Lo que hace especial a PokeFisi desde el punto de vista académico es que implementa **agentes inteligentes** que toman decisiones de forma autónoma usando diferentes estrategias: desde elecciones completamente aleatorias hasta una **función heurística** que evalúa el estado del juego y elige la acción más conveniente.

---

## 2. Conceptos básicos para nuevos jugadores

Si nunca jugaste Pokémon, aquí están los conceptos que necesitas entender antes de empezar.

### Pokémon

Un Pokémon es una criatura con cuatro estadísticas que determinan su desempeño en combate:

| Estadística | Abreviatura | Qué representa |
|---|---|---|
| Puntos de Salud | HP | Cuánto daño puede recibir antes de caer. Cuando llega a 0 el Pokémon queda fuera de combate. |
| Ataque | ATK | Qué tan fuerte pega. A mayor ataque, más daño causa con sus movimientos. |
| Defensa | DEF | Qué tan bien resiste el daño recibido. A mayor defensa, menos daño sufre. |
| Velocidad | SPE | Qué tan rápido actúa. El Pokémon más veloz ataca primero en cada turno. |

### Tipos

Cada Pokémon pertenece a uno o dos **tipos** (Fuego, Agua, Planta, Eléctrico, etc.). Los tipos crean ventajas y desventajas entre sí: el Fuego es fuerte contra Planta, el Agua es fuerte contra Fuego, etc. Elegir el tipo correcto puede duplicar el daño causado.

### Movimientos

Cada Pokémon tiene hasta **4 movimientos** disponibles por batalla. Cada movimiento tiene:
- **Tipo**: determina las ventajas de tipo
- **Poder Base (BP)**: cuánto daño base causa
- **Precisión (Acc)**: probabilidad de que el ataque no falle (en %)

### Turno

En cada turno, ambos jugadores eligen una acción simultáneamente. Las opciones son:
- **Atacar**: usar uno de los 4 movimientos disponibles
- **Cambiar Pokémon**: retirar el Pokémon activo y enviar otro del equipo

El Pokémon más rápido actúa primero. Si un Pokémon queda con 0 HP, el jugador debe enviar otro automáticamente. La batalla termina cuando un jugador se queda sin Pokémon en pie.

---

## 3. Cómo jugar — Modo GUI

### Paso 1 — Menú Principal

Al ejecutar `python3 main.py --gui` aparece el menú principal con el botón **NUEVA BATALLA**. Haz clic para comenzar.

### Paso 2 — Selección de Modo

Elige entre dos modos:

- **HUMANO vs IA**: tú controlas el Jugador 1 y una IA controla al Jugador 2.
- **IA vs IA**: dos agentes de IA se enfrentan automáticamente. Puedes observar la batalla en tiempo real.

Después selecciona qué tipo de IA quieres enfrentar usando los botones `<` y `>`. La pantalla muestra en tiempo real para cada agente seleccionado:

- **Descripción** de su estrategia.
- **Pesos verticales** (para Heurística Avanzada y agentes entrenados): cada factor aparece en su propia fila con una barra de color proporcional a su valor, lo que permite comparar visualmente los dos agentes en modo IA vs IA.
- **Win-rate de entrenamiento** si el agente fue generado mediante el proceso de entrenamiento.

Agentes disponibles:

- **Agente Aleatorio**: elige acciones completamente al azar.
- **Heurística Básica**: evalúa el estado del juego y elige la acción más inteligente según su HP.
- **Heurística Avanzada**: evalúa 6 factores ponderados del equipo completo.
- **HeuristicaAvanzada-N**: agente entrenado con N batallas. Solo aparece si previamente lo entrenaste desde la consola.

Por último elige el tamaño del equipo: **3 vs 3** o **4 vs 4**.

### Paso 3 — Selección de Pokémon

Aparece una cuadrícula con los 30 Pokémon disponibles. Cada tarjeta muestra:
- Nombre del Pokémon
- Tipo(s) con su color correspondiente
- Estadísticas: HP, ATK, DEF, SPE

**Cómo navegar:**
- Usa la **rueda del ratón** para hacer scroll y ver todos los Pokémon
- También puedes arrastrar la **barra lateral derecha**

**Cómo seleccionar:**
- Haz clic en un Pokémon para añadirlo a tu equipo (se resalta en verde)
- Haz clic de nuevo para deseleccionarlo
- La franja superior muestra los slots de tu equipo en tiempo real

Cuando completes tu equipo, la pantalla cambia automáticamente para que elijas el equipo rival (en modo Humano vs IA, tú decides con qué Pokémon te enfrentarás). Una vez ambos equipos estén listos, el botón **INICIAR BATALLA** se activa.

### Paso 4 — La Batalla

La pantalla de combate se divide en dos zonas:

**Zona superior (campo de batalla):**
- El Pokémon enemigo (Jugador 2) aparece arriba a la izquierda con su nombre, tipo, barra de HP y HP numérico.
- Tu Pokémon (Jugador 1) aparece abajo a la derecha con la misma información.
- Los puntos de colores debajo del nombre indican cuántos Pokémon quedan vivos en cada equipo (verde = vivo, rojo = derrotado).

**Zona inferior:**
- A la izquierda: el **log de batalla**, que narra todo lo que ocurre turno a turno.
- A la derecha: los **botones de movimiento** con el nombre, tipo, Poder Base y Precisión de cada ataque, más el botón **CAMBIAR POKEMON**.

**Barra de HP:**
- Verde: más del 50% de vida
- Amarilla: entre 25% y 50% de vida
- Roja: menos del 25% de vida (¡peligro!)

**En modo IA vs IA:** los botones están deshabilitados. La batalla ocurre automáticamente con una pausa de 1.5 segundos entre turnos para que puedas seguirla.

Al terminar la batalla, presiona cualquier tecla para ver la pantalla de resultados con el ganador y las estadísticas.

---

## 4. Cómo jugar — Modo Consola

Ejecuta `python3 main.py --console` (Linux) o `python main.py --console` (Windows).

### Menú principal

```
╔══════════════════════════════════════╗
║           POKEFISI  🎮              ║
╠══════════════════════════════════════╣
║  1. Humano vs IA                     ║
║  2. IA vs IA                         ║
║  3. Entrenar Heuristica Avanzada     ║
║  4. Salir                            ║
╚══════════════════════════════════════╝
Elige una opcion: _
```

Escribe el número y presiona `Enter`.

La opción **3** lanza el proceso de entrenamiento: pide el número de batallas, muestra el progreso en tiempo real y guarda los pesos resultantes automáticamente.

### Selección de Pokémon

El juego muestra una tabla con todos los Pokémon numerados del 1 al 30. Escribe los IDs separados por espacios:

```
Elige 3 Pokémon (IDs separados por espacios): 5 9 7
```

Esto selecciona a Mewtwo (5), Dragonite (9) y Machamp (7).

### Durante la batalla

Cada turno muestra el estado actual con barras de HP, los Pokémon de cada equipo y las opciones disponibles:

```
  1. Flamethrower    (Fire,   Base 90,  Acc 100%)
  2. Dragon Claw     (Dragon, Base 80,  Acc 100%)
  3. Fly             (Flying, Base 90,  Acc 95%)
  4. Hurricane       (Flying, Base 110, Acc 70%)
  5. Cambiar a Blastoise
```

Escribe el número de la acción y presiona `Enter`. Después de cada turno, el log muestra exactamente qué pasó: qué movimiento se usó, el multiplicador de tipo, el daño causado y los HP restantes.

---

## 5. Los 30 Pokémon disponibles

Todos los Pokémon y sus estadísticas están definidos en `data/pokemon.json`. La siguiente tabla los lista con sus stats base:

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

> **Consejo para nuevos jugadores:** Mewtwo (5), Dragonite (9) y Snorlax (11) son los más poderosos en términos de estadísticas. Machamp (7), Flareon (16) y Rhydon (17) tienen el ATK más alto del roster.

---

## 6. Los movimientos y sus estadísticas

Cada Pokémon tiene asignados entre 5 y 7 movimientos en `data/pokemon.json` (campo `move_ids`). Al inicio de cada batalla se seleccionan **4 de ellos al azar** para ese combate. Esto añade variabilidad y hace que cada batalla sea diferente.

Los movimientos están definidos en `data/moves.json`. Cada uno tiene la siguiente estructura:

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

| Campo | Significado |
|---|---|
| `id` | Identificador único del movimiento |
| `name` | Nombre del movimiento |
| `type` | Tipo del movimiento (determina ventajas de tipo) |
| `base_power` | Poder base usado en la fórmula de daño |
| `accuracy` | Probabilidad de acierto en porcentaje (100 = nunca falla) |
| `category` | `physical` o `special` (actualmente ambos usan la misma fórmula) |
| `effect` | Efecto secundario (registrado pero no activo en esta versión) |

En el código, la clase `Move` en `engine/move.py` carga estos datos:

```python
# engine/move.py
class Move:
    def __init__(self, data: dict):
        self.id         = data["id"]
        self.name       = data["name"]
        self.type       = data["type"]
        self.base_power = data["base_power"]
        self.accuracy   = data["accuracy"]
        self.category   = data["category"]
        self.effect     = data.get("effect", "none")
```

Y en `engine/pokemon.py`, la selección aleatoria de 4 movimientos ocurre en el constructor:

```python
# engine/pokemon.py  (línea 22)
self.moves = random.sample(available, min(4, len(available)))
```

---

## 7. La fórmula de daño

Este es el corazón del motor de combate. Está implementada en `engine/damage.py` y define exactamente cuánto daño causa un ataque.

### La fórmula

```
Damage = (Attack / Defense_op) * BasePower - Speed_op * K
```

| Variable | Descripción |
|---|---|
| `Attack` | Estadística de Ataque del Pokémon atacante |
| `Defense_op` | Estadística de Defensa del Pokémon defensor |
| `BasePower` | Poder base del movimiento usado |
| `Speed_op` | Estadística de Velocidad del Pokémon defensor |
| `K` | Factor de ajuste global, definido en `config.py` como `K = 0.5` |

### ¿Qué hace cada parte?

- **`(Attack / Defense_op) * BasePower`**: el núcleo del daño. Cuanto mayor sea el ataque del atacante y menor la defensa del defensor, más daño. El poder del movimiento amplifica este cociente.
- **`- Speed_op * K`**: la velocidad del defensor reduce el daño, simulando que un Pokémon rápido esquiva parcialmente el golpe. Con K=0.5, un defensor con 100 de velocidad reduce 50 puntos de daño bruto.

### Reglas adicionales

1. **Daño mínimo**: si el cálculo da menos de 1, el daño se fija en 1. Un ataque nunca puede curar al defensor ni hacer 0 daño (salvo inmunidad de tipo).
2. **Precisión**: antes del cálculo se lanza un número aleatorio entre 1 y 100. Si supera la precisión del movimiento, el ataque falla y el daño es 0.
3. **Multiplicador de tipo**: el daño final se multiplica según la relación de tipos.

### Implementación en el código

```python
# engine/damage.py  (líneas 89-108)
def calculate_damage(attacker, move, defender) -> tuple[int, float]:
    # 1. Verificar precisión
    if random.randint(1, 100) > move.accuracy:
        return 0, 1.0  # fallo — daño cero

    # 2. Calcular daño bruto con la fórmula
    raw = (attacker.attack / max(1, defender.defense)) * move.base_power - defender.speed * K
    raw = max(1, raw)  # daño mínimo garantizado

    # 3. Aplicar multiplicador de tipo
    multiplier = get_type_multiplier(move.type, defender.types)
    final = int(raw * multiplier)
    final = max(0, final)  # inmunidad total → 0

    return final, multiplier
```

### Ejemplo concreto

Machamp (ATK=130) usa **Close Combat** (BP=120) contra Pikachu (DEF=40, SPE=90):

```
raw   = (130 / 40) * 120 - 90 * 0.5
      = 3.25 * 120 - 45
      = 390 - 45
      = 345

tipo  = Fighting → Electric  → x1.0 (neutro)

final = 345 * 1.0 = 345 daño
```

Con 35 HP, Pikachu cae en un solo golpe.

---

## 8. Ventajas y desventajas de tipo

La tabla de tipos está definida en `engine/damage.py` como el diccionario `TYPE_CHART`. Para cada tipo atacante, define qué multiplicador aplica contra cada tipo defensor:

| Resultado | Multiplicador | Mensaje en pantalla |
|---|---|---|
| Superefectivo | ×2.0 | ¡Muy efectivo! |
| Normal | ×1.0 | (sin mensaje) |
| Poco efectivo | ×0.5 | Poco efectivo. |
| Inmune | ×0.0 | No afecta... |

Si un Pokémon tiene **dos tipos**, los multiplicadores se **multiplican entre sí**. Por ejemplo, un movimiento de tipo Hielo contra un Pokémon Dragon/Volador aplica ×2.0 (Dragon) × ×2.0 (Volador) = **×4.0** de daño total.

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

### Implementación en el código

La función `get_type_multiplier` recorre todos los tipos del defensor y multiplica:

```python
# engine/damage.py  (líneas 81-86)
def get_type_multiplier(attack_type: str, defender_types: list[str]) -> float:
    multiplier = 1.0
    chart = TYPE_CHART.get(attack_type, {})
    for def_type in defender_types:
        multiplier *= chart.get(def_type, 1.0)
    return multiplier
```

Si el tipo atacante no está en `TYPE_CHART` o la combinación no tiene entrada definida, el multiplicador es 1.0 (neutral).

---

## 9. Inteligencia Artificial — Los Agentes

### Arquitectura base

Todos los agentes heredan de la clase abstracta `Agent` en `ai/base_agent.py`. Esta clase define el contrato que cualquier agente debe cumplir:

```python
# ai/base_agent.py
class Agent(ABC):
    @abstractmethod
    def choose_action(self, state: BattleState, player_id: int) -> dict:
        ...
```

El método `choose_action` recibe el **estado completo de la batalla** y el **ID del jugador** (1 o 2), y debe devolver una acción en uno de estos dos formatos:

```python
{"type": "move",   "move_index": 0}   # usar el movimiento en la posición 0
{"type": "switch", "pokemon_index": 2} # cambiar al Pokémon en la posición 2
```

La clase base también provee el método `_possible_actions`, que lista todas las acciones válidas en un momento dado: los 4 movimientos disponibles más todos los cambios posibles (Pokémon vivos que no sea el activo):

```python
# ai/base_agent.py  (líneas 27-35)
def _possible_actions(self, state: BattleState, player_id: int) -> list[dict]:
    actions = []
    active = state.get_active(player_id)
    for i in range(len(active.get_available_moves())):
        actions.append({"type": "move", "move_index": i})
    for i, p in enumerate(state.get_team(player_id)):
        if p.is_alive() and i != state.get_active_index(player_id):
            actions.append({"type": "switch", "pokemon_index": i})
    return actions if actions else [{"type": "move", "move_index": 0}]
```

---

### Agente 1 — Aleatorio (`ai/random_agent.py`)

El agente más simple posible. No evalúa nada: simplemente toma todas las acciones posibles y elige una completamente al azar.

```python
# ai/random_agent.py
class RandomAgent(Agent):
    def choose_action(self, state: BattleState, player_id: int) -> dict:
        return random.choice(self._possible_actions(state, player_id))
```

**Por qué existe:** sirve como **línea base** de comparación. Si un agente más inteligente no gana al menos el 60-70% de las veces contra el agente aleatorio, su heurística no está funcionando bien. Es el punto de referencia mínimo.

**Comportamiento esperado:** aproximadamente 50% de victorias en batallas simétricas. Sus derrotas son frecuentes porque puede usar movimientos inefectivos, atacar con el tipo incorrecto o cambiar de Pokémon sin ningún motivo estratégico.

---

### Agente 2 — Heurística Básica (`ai/heuristic_basic.py`)

Este agente implementa una **función heurística** para evaluar el estado del juego y tomar decisiones informadas. Es el núcleo de la inteligencia artificial del proyecto.

#### ¿Qué es una función heurística?

Una heurística es una función que recibe el estado actual del juego y devuelve un número. Cuanto mayor el número, mejor es esa situación para el agente. El agente usa esta función para comparar todas las acciones posibles y elegir la que lleva al mejor estado.

#### La función de evaluación

```python
# ai/heuristic_basic.py  (líneas 10-13)
def _evaluate(self, state: BattleState, player_id: int) -> float:
    me  = state.get_active(player_id)
    opp = state.get_active(3 - player_id)
    return me.hp_ratio() - opp.hp_ratio()
```

La fórmula es:

```
score = (HP_propio / HP_máx_propio) - (HP_oponente / HP_máx_oponente)
```

Ambos términos están **normalizados entre 0 y 1** gracias al método `hp_ratio()` de la clase `Pokemon`:

```python
# engine/pokemon.py  (línea 39-40)
def hp_ratio(self) -> float:
    return self.current_hp / self.max_hp
```

**Interpretación del score:**
- `score = 1.0`: yo tengo vida completa y el oponente está a 0 HP (situación ideal)
- `score = 0.0`: ambos tienen el mismo porcentaje de vida (equilibrio)
- `score = -1.0`: yo estoy a 0 HP y el oponente tiene vida completa (situación crítica)

#### El proceso de decisión

El agente no se limita a evaluar el estado actual. Para cada acción posible, **simula mentalmente** qué pasaría si la ejecutara y luego evalúa el estado resultante:

```python
# ai/heuristic_basic.py  (líneas 15-27)
def choose_action(self, state: BattleState, player_id: int) -> dict:
    best_score  = float("-inf")
    best_action = None

    for action in self._possible_actions(state, player_id):
        sim = state.copy()                          # copia el estado actual
        self._apply_action(sim, player_id, action)  # simula la acción
        score = self._evaluate(sim, player_id)      # evalúa el resultado
        if score > best_score:
            best_score  = score
            best_action = action

    return best_action
```

Paso a paso:
1. Lista todas las acciones posibles (movimientos + cambios de Pokémon)
2. Para cada acción, hace una **copia profunda** del estado con `state.copy()`
3. Aplica la acción sobre la copia sin modificar el estado real
4. Evalúa el estado resultante con la función heurística
5. Se queda con la acción que produce el score más alto
6. Devuelve esa acción como su decisión

#### La simulación de acciones

La simulación calcula el daño esperado sin azar (no verifica precisión en la copia):

```python
# ai/heuristic_basic.py  (líneas 29-39)
def _apply_action(self, state: BattleState, player_id: int, action: dict):
    if action["type"] == "switch":
        state.set_active_index(player_id, action["pokemon_index"])
        return
    move_index = action["move_index"]
    attacker   = state.get_active(player_id)
    defender   = state.get_active(3 - player_id)
    moves      = attacker.get_available_moves()
    if move_index < len(moves):
        dmg, _ = calculate_damage(attacker, moves[move_index], defender)
        defender.take_damage(dmg)
```

Nota importante: al simular, el agente llama a `calculate_damage` que sí incluye el factor de precisión aleatorio. Esto significa que en la simulación, un movimiento puede "fallar" y el agente podría subestimar su valor. Es una limitación de la heurística básica que una versión más avanzada podría corregir calculando el daño esperado sin aleatoriedad.

#### ¿Por qué esta heurística es mejor que el agente aleatorio?

El agente aleatorio puede usar un movimiento de tipo Agua contra un Pokémon de tipo Agua (×0.5 de daño, muy ineficiente). La heurística básica **siempre elige el movimiento que cause más daño** porque mayor daño → menor HP del oponente → score más alto.

También considera los cambios de Pokémon: si cambiar a otro Pokémon del equipo resulta en un estado mejor (por ejemplo, sacar un Pokémon que se va a morir y poner uno con más HP), la heurística lo detecta y realiza el cambio.

---

### Agente 3 — Heurística Avanzada (`ai/heuristic_advanced.py`)

Este agente amplía la heurística básica considerando el **equipo completo** en lugar de solo el Pokémon activo, e incorpora cuatro factores adicionales: ventaja de tipo, diferencia de velocidad, porcentaje de Pokémon vivos propios y rivales.

#### La función de evaluación de 6 factores

```python
# ai/heuristic_advanced.py  (líneas 66-73)
w = self.weights
return (
      w[0] * alive_mine       # fracción de mis Pokémon vivos
    + w[1] * hp_avg_mine      # HP promedio propio normalizado
    - w[2] * hp_avg_opp       # HP promedio rival normalizado
    + w[3] * type_adv         # mejor ventaja de tipo disponible / 4.0
    + w[4] * speed_norm       # diferencia de velocidad normalizada a [0,1]
    - w[5] * alive_opp        # fracción de Pokémon vivos del rival
)
```

Todos los factores están normalizados en `[0, 1]` para que los pesos sean comparables entre sí.

| Factor | Cálculo | ¿Por qué importa? |
|---|---|---|
| `alive_mine` | vivos_propios / total | Más Pokémon vivos = más opciones tácticas |
| `hp_avg_mine` | media de hp_ratio() del equipo | Mide la resistencia global del equipo |
| `hp_avg_opp` | media de hp_ratio() rival | Cuanto más bajo, más cerca de ganar |
| `type_adv` | mejor multiplicador disponible / 4.0 | Explotar ventajas de tipo es clave |
| `speed_norm` | (speed_diff + MAX_SPE) / (2 · MAX_SPE) | Actuar primero da ventaja táctica |
| `alive_opp` | vivos_rivales / total | Reducir el equipo rival acelera la victoria |

Los **pesos por defecto** son `[0.30, 0.25, 0.25, 0.10, 0.05, 0.05]`. Se pueden ajustar manualmente en `config.py` o mediante el entrenamiento automático.

#### Ventaja de tipo

El factor `type_adv` se calcula buscando el mayor multiplicador de tipo entre todos los movimientos disponibles del Pokémon activo:

```python
# ai/heuristic_advanced.py  (líneas 75-82)
def _best_type_advantage(self, me, opp) -> float:
    best = 0.0
    for move in me.get_available_moves():
        mult = get_type_multiplier(move.type, opp.types)
        if mult > best:
            best = mult
    return best
```

Esto incentiva al agente a elegir movimientos superefectivos o al menos a cambiar a un Pokémon con mejor cobertura de tipo.

---

### Agente 4 — Heurística Entrenada (`ai/heuristic_trained.py`)

Es una subclase de `HeuristicAdvancedAgent` que en lugar de usar los pesos por defecto, **carga pesos optimizados** desde un archivo JSON generado por el proceso de entrenamiento.

```python
# ai/heuristic_trained.py
class HeuristicTrainedAgent(HeuristicAdvancedAgent):
    def __init__(self, weights_file: str):
        with open(weights_file) as f:
            data = json.load(f)
        super().__init__(weights=data["weights"])
        self.name = f"HeuristicaAvanzada-{data['battles']}"
        self.battles_trained = data["battles"]
        self.win_rate_training = data.get("win_rate", 0.0)
```

Su lógica de decisión es idéntica a la Heurística Avanzada; la única diferencia son los pesos. Los pesos aprendidos reflejan qué factores resultaron más predictivos de victorias durante el entrenamiento.

---

### El estado de la batalla (`engine/state.py`)

La clase `BattleState` es la pieza central que conecta todo. Representa una **fotografía completa** del estado actual de la batalla en un momento dado.

```python
# engine/state.py
class BattleState:
    def __init__(self, team1: list, team2: list):
        self.player1_team    = team1          # lista de Pokémon del J1
        self.player2_team    = team2          # lista de Pokémon del J2
        self.active_index_p1 = 0              # índice del Pokémon activo J1
        self.active_index_p2 = 0              # índice del Pokémon activo J2
        self.turn_number     = 0              # número de turno actual
```

Los métodos más importantes:

| Método | Qué hace |
|---|---|
| `is_terminal()` | Devuelve `True` si algún equipo perdió todos sus Pokémon |
| `get_winner()` | Devuelve 1, 2 o None según quién ganó |
| `copy()` | Hace una copia profunda del estado completo (usado por la IA para simular) |
| `next_alive_index()` | Encuentra el siguiente Pokémon vivo de un equipo |

El método `copy()` usa `copy.deepcopy()` de Python, que crea duplicados independientes de todos los objetos dentro del estado. Esto es esencial para que la IA pueda simular acciones sin alterar el estado real de la batalla.

```python
# engine/state.py  (línea 59-60)
def copy(self):
    return copy.deepcopy(self)
```

---

## 10. Entrenamiento de la IA — Stochastic Hill-Climbing

El entrenamiento busca los pesos que maximizan el win-rate de la Heurística Avanzada enfrentándola contra una mezcla de oponentes. El algoritmo usado se llama **Stochastic Hill-Climbing** (escalada estocástica de colinas).

### Idea general

Imagina los 6 pesos como una posición en un espacio de 6 dimensiones. El objetivo es encontrar el punto de ese espacio donde el agente gana más batallas. Para eso el algoritmo:

1. Parte de una posición conocida (los pesos por defecto).
2. Da un paso aleatorio pequeño (perturba los pesos con ruido gaussiano).
3. Si el nuevo punto es mejor (ganó la batalla), se mueve allí.
4. Si es peor (perdió), vuelve al punto anterior.
5. Repite N veces.

### Enfriamiento de la temperatura

El tamaño del paso disminuye con el tiempo siguiendo una función exponencial:

```python
# ai/trainer.py  (línea 43)
t = 0.12 * math.exp(-3.5 * i / n_battles)
```

Al inicio (`i=0`): `t ≈ 0.12` → pasos grandes, exploración amplia del espacio de pesos.
Al final (`i=N`): `t ≈ 0.005` → pasos pequeños, refinamiento de la solución encontrada.

Este esquema se llama **simulated annealing** y evita que el algoritmo quede atrapado en óptimos locales al principio, mientras converge a una solución estable al final.

### Perturbación y normalización de pesos

En cada batalla, los pesos candidatos se generan así:

```python
# ai/trainer.py  (líneas 45-48)
candidate = [max(0.005, w + random.gauss(0, t)) for w in current_w]
total = sum(candidate)
candidate = [w / total for w in candidate]  # normalizar para que sumen 1
```

1. A cada peso se le suma ruido gaussiano con desviación estándar `t`.
2. Se fuerza un mínimo de 0.005 para que ningún factor quede completamente ignorado.
3. Se normalizan para que la suma sea 1, manteniendo la interpretación de "fracción del score".

### Oponentes mixtos

El agente se enfrenta alternando dos rivales:
- **Batallas pares** (`i % 2 == 0`): contra `RandomAgent`.
- **Batallas impares** (`i % 2 == 1`): contra `HeuristicBasicAgent`.

Esta mezcla evita que los pesos se sobreajusten a un único estilo de juego y produce un agente más robusto.

### Selección de los mejores pesos

Los pesos que se guardan no son los del último paso, sino los de la **ventana deslizante con mayor win-rate**:

```python
# ai/trainer.py  (líneas 57-62)
window.append(1 if won else 0)
if len(window) > 20:
    window.pop(0)
wr_window = sum(window) / len(window)
if wr_window >= best_wr and len(window) >= 10:
    best_wr = wr_window
    best_w = current_w[:]
```

Esto protege contra rachas de suerte: un agente que gana 20 batallas seguidas y luego pierde 10 no sobreescribe a uno que mantuvo una tasa del 70% de forma consistente.

### Ejemplo de output durante el entrenamiento

```
  Entrenando 200 batallas vs Random (50%) y HeuristicBasica (50%)...

  [ 10%] Batalla  20/200  |  Win-rate: 65.0%  |  Temp: 0.0931
  [ 20%] Batalla  40/200  |  Win-rate: 67.5%  |  Temp: 0.0691
  ...
  [100%] Batalla 200/200  |  Win-rate: 74.0%  |  Temp: 0.0064

  Entrenamiento completado!
  Guardado en:  data/weights_200.json
  Agente:       HeuristicaAvanzada-200
  Win-rate:     74.0%

  Pesos aprendidos (vs base):
    alive_mine      0.3381  (base 0.300,  +0.0381)
    hp_avg_mine     0.2715  (base 0.250,  +0.0215)
    hp_avg_opp      0.2194  (base 0.250,  -0.0306)
    type_adv        0.0982  (base 0.100,  -0.0018)
    speed_norm      0.0431  (base 0.050,  -0.0069)
    alive_opp       0.0297  (base 0.050,  -0.0203)
```

### Formato del archivo de pesos

El archivo `data/weights_N.json` tiene la siguiente estructura:

```json
{
  "weights": [0.338, 0.271, 0.219, 0.098, 0.043, 0.031],
  "battles": 200,
  "win_rate": 0.74
}
```

El orden de los pesos corresponde siempre a: `[alive_mine, hp_avg_mine, hp_avg_opp, type_adv, speed_norm, alive_opp]`.

### Registro automático de agentes (`ai/registry.py`)

Al iniciar el juego (GUI o consola), el registro escanea `data/weights_*.json` y añade automáticamente cada agente entrenado a la lista de selección:

```python
# ai/registry.py
def build_registry():
    return _BASE + _trained_entries()   # base + todos los weights_*.json encontrados
```

Esto significa que cualquier archivo de pesos que coloques en `data/` estará disponible como agente sin necesidad de modificar el código.

---

## 11. Arquitectura del código

El proyecto sigue una arquitectura en capas donde cada módulo tiene una responsabilidad clara y no depende de módulos de capas superiores.

```
main.py
    │
    ├── gui/game_manager.py          ← orquesta la GUI
    │       └── gui/screens/         ← pantallas individuales
    │       └── gui/components/      ← componentes visuales reutilizables
    │
    ├── console/console_menu.py      ← orquesta el modo texto + entrenamiento
    │       └── console/...          ← selección y batalla en texto
    │
    ├── ai/                          ← agentes de IA
    │       ├── base_agent.py        ← contrato abstracto (+ get_info_lines)
    │       ├── random_agent.py      ← nivel 1
    │       ├── heuristic_basic.py   ← nivel 2
    │       ├── heuristic_advanced.py← nivel 3 (6 factores ponderados)
    │       ├── heuristic_trained.py ← carga pesos desde weights_N.json
    │       ├── trainer.py           ← bucle de entrenamiento hill-climbing
    │       └── registry.py          ← registro dinámico de todos los agentes
    │
    └── engine/                      ← motor de combate (sin GUI ni IA)
            ├── pokemon.py           ← clase Pokémon
            ├── move.py              ← clase Movimiento
            ├── damage.py            ← fórmula de daño + tabla de tipos
            ├── state.py             ← estado de la batalla
            ├── battle.py            ← flujo de turnos
            └── loader.py            ← carga de datos JSON
```

**Principio clave:** el módulo `engine/` no sabe nada de pygame, consola ni IA. Funciona solo con datos. Los agentes de IA tampoco saben de pygame. Esto hace que cualquier mejora al motor beneficie automáticamente a todos los modos.

### Archivo de configuración (`config.py`)

Centraliza todas las constantes del proyecto para poder ajustarlas en un solo lugar:

```python
# config.py
K          = 0.5    # factor de velocidad en la fórmula de daño
FPS        = 60     # cuadros por segundo de la GUI
AI_TURN_DELAY = 1500  # pausa entre turnos en IA vs IA (milisegundos)
```

Si quieres experimentar con la fórmula de daño, cambiar `K` aquí afecta a toda la simulación sin tocar ningún otro archivo.

---

## 12. Flujo completo de una batalla

Entender el flujo de una batalla ayuda a comprender cómo el código conecta todas las piezas.

### Inicio

1. Se cargan los datos desde `data/pokemon.json` y `data/moves.json` mediante `engine/loader.py`
2. Se construyen los equipos: cada `Pokemon` selecciona 4 movimientos al azar de su pool
3. Se crea un `BattleState` con ambos equipos
4. Se instancian los agentes (humano implícito o `RandomAgent` / `HeuristicBasicAgent`)
5. Se crea un objeto `Battle` que une el estado con los dos agentes

### Cada turno (`engine/battle.py` → método `step`)

```
1. Incrementar turno_number
2. Agente 1 → choose_action(state, 1)  → action1
3. Agente 2 → choose_action(state, 2)  → action2
4. Comparar velocidades de los Pokémon activos:
   - El más rápido ejecuta su acción primero
5. Ejecutar acción del primero:
   - Si es "move": calculate_damage → take_damage → registrar en log
   - Si es "switch": cambiar Pokémon activo
6. Si la batalla no terminó, ejecutar acción del segundo
7. Si algún Pokémon cayó (HP=0): reemplazar automáticamente con el siguiente vivo
8. Devolver las líneas de log generadas en este turno
```

### Condición de fin

```python
# engine/state.py  (líneas 44-48)
def is_terminal(self) -> bool:
    return (
        all(not p.is_alive() for p in self.player1_team)
        or all(not p.is_alive() for p in self.player2_team)
    )
```

La batalla termina cuando **todos** los Pokémon de un equipo tienen 0 HP.

### Diagrama simplificado

```
Battle.run()
    └─ while not is_terminal():
           └─ step()
                  ├─ agent1.choose_action()   ← IA evalúa o humano hace clic
                  ├─ agent2.choose_action()   ← IA evalúa o humano hace clic
                  ├─ ordenar por velocidad
                  ├─ _execute_action(primero)
                  │       └─ calculate_damage() → take_damage()
                  ├─ _execute_action(segundo)
                  │       └─ calculate_damage() → take_damage()
                  └─ _auto_replace() para ambos
    └─ get_winner()
```

---

## 13. Estrategias recomendadas

### Para ganar al Agente Aleatorio

Cualquier estrategia básica funciona. Presta atención a los tipos y usa siempre el movimiento superefectivo cuando lo tengas disponible.

### Para ganar a la Heurística Básica

La heurística solo mira el HP inmediato. No predice más de un turno. Puedes vencerla:

- **Sacrificando un Pokémon débil** para hacer un cambio ventajoso: la IA no lo anticipa.
- **Usando un Pokémon lento pero muy defensivo** (como Slowbro o Rhydon): su alta defensa hace que el daño calculado por la heurística sea menor del esperado.
- **Eligiendo movimientos de alta precisión** sobre movimientos de alto poder: si la IA usa Hydro Pump (BP=110, Acc=80%) y falla, pierdes un turno y el humano puede aprovechar.

### Para ganar a la Heurística Avanzada

Esta IA considera el equipo completo y la ventaja de tipo. Es más difícil de sorprender:

- **Diversifica los tipos de tu equipo**: si tus tres Pokémon son todos del mismo tipo, la IA encontrará fácilmente un movimiento superefectivo contra todos.
- **Prioriza Pokémon rápidos**: la IA pondera la velocidad; un equipo con alta SPE le da menos ventaja.
- **Cambia de Pokémon estratégicamente**: la IA no simula la respuesta de tu cambio, solo el estado inmediato.

### Para ganar a un agente entrenado

Depende de cómo resultaron sus pesos. Observa los pesos en la pantalla de selección:

- Si `type_adv` es alto, el agente prioriza mucho la ventaja de tipo: construye un equipo con cobertura de tipos variada.
- Si `vel` es alto, el agente valora mucho actuar primero: usa Pokémon de alta velocidad.
- Si `hp_avg_opp` (negativo en la fórmula) tiene peso bajo, el agente no presiona agresivamente el daño: un equipo defensivo puede aguantar y desgastarlo.

### Equipos equilibrados sugeridos para comenzar

**Equipo ofensivo:**
- Mewtwo (5) — Psychic puro, altísimo ATK y SPE
- Dragonite (9) — Dragon/Flying, el mayor ATK del roster
- Machamp (7) — Fighting, ATK=130, bueno contra Normal y Rock

**Equipo equilibrado:**
- Lapras (10) — Water/Ice, el mayor HP del roster (130)
- Arcanine (12) — Fire, buena velocidad y ataque
- Alakazam (8) — Psychic, la mayor velocidad del grupo con SPE=120

**Equipo defensivo:**
- Snorlax (11) — Normal, HP=160, el tanque definitivo
- Slowbro (29) — Water/Psychic, DEF=110
- Rhydon (17) — Ground/Rock, DEF=120

---

*Manual de PokeFisi — Proyecto académico de Inteligencia Artificial*
