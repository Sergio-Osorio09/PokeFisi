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
10. [Entrenamiento de la IA — Hill-Climbing y Algoritmo Genético](#10-entrenamiento-de-la-ia--hill-climbing-y-algoritmo-genético)
11. [Arquitectura del código](#11-arquitectura-del-código)
12. [Flujo completo de una batalla](#12-flujo-completo-de-una-batalla)
13. [Estrategias recomendadas](#13-estrategias-recomendadas)
14. [El panel cerebro — cómo leer el razonamiento de la IA](#14-el-panel-cerebro--cómo-leer-el-razonamiento-de-la-ia)
15. [Comandos del juego y funciones que los implementan](#15-comandos-del-juego-y-funciones-que-los-implementan)

---

## 1. ¿Qué es PokeFisi?

PokeFisi es un simulador de combates por turnos inspirado en Pokémon. Dos jugadores (humanos o agentes de Inteligencia Artificial) se enfrentan con equipos de 3 o 4 Pokémon. El objetivo es derrotar a todos los Pokémon del equipo rival.

Lo que hace especial a PokeFisi desde el punto de vista académico es que implementa **agentes inteligentes** que toman decisiones de forma autónoma con estrategias de complejidad creciente: desde elecciones **aleatorias**, pasando por **funciones heurísticas** que evalúan el estado del juego, hasta **búsqueda adversaria (minimax con poda alfa-beta)** y un **algoritmo genético** que optimiza la evaluación del minimax.

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

Al ejecutar `python3 main.py --gui` aparece el menú principal con cuatro botones: **NUEVA BATALLA** (jugar), **ENTRENAR IA GENETICA** (evolucionar un agente, ver sección 10), **ELIMINAR IAS ENTRENADAS** (borrar pesos guardados —heurísticas y genéticos— con confirmación) y **SALIR**. Haz clic en `NUEVA BATALLA` para comenzar.

### Paso 2 — Selección de Modo

Elige entre dos modos:

- **HUMANO vs IA**: tú controlas el Jugador 1 y una IA controla al Jugador 2.
- **IA vs IA**: dos agentes de IA se enfrentan automáticamente. Puedes observar la batalla en tiempo real.

Después selecciona qué tipo de IA quieres enfrentar usando los botones `<` y `>`. La pantalla muestra en tiempo real para cada agente seleccionado:

- **Descripción** de su estrategia.
- **Pesos** (heurísticas y entrenados) o una **tabla de capacidades** (Minimax y Genético: profundidad, velocidad, fitness…) para comparar visualmente las opciones.
- **Win-rate de entrenamiento** si el agente fue generado mediante un proceso de entrenamiento.

Agentes disponibles:

- **Agente Aleatorio**: elige acciones completamente al azar.
- **Heurística Básica**: elige la acción que maximiza `HP_propio − HP_rival` del Pokémon activo.
- **Heurística Avanzada**: evalúa **4 diferenciales** ponderados (supervivencia, HP, tipo, velocidad).
- **Heurística Mejorada**: evalúa **6 componentes** (supervivencia, HP ponderado, amenaza de KO, peligro de KO, cobertura de tipos y velocidad).
- **Minimax `d=2` / `d=3`**: búsqueda adversaria con poda alfa-beta que anticipa la respuesta del rival hasta `d` turnos.
- **Expectimax `d=2`**: variante que modela al rival (por defecto la Básica) en vez de asumir el peor caso; capta mejor la simultaneidad.
- **Genético**: el Minimax con los pesos de su evaluación optimizados por un algoritmo genético.
- **HeuristicaAvanzada-N / H.Mejorada-N / Genetico g…**: agentes entrenados; aparecen solo si previamente los generaste.

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

**Panel cerebro (columna derecha):** cuando un jugador es una IA, se muestra en tiempo real qué está evaluando en el turno actual: las acciones consideradas con su puntuación; para el Minimax, además, los **nodos explorados, las podas alfa-beta** y la variante principal (mi mejor acción → mejor réplica del rival); para el Genético, también sus pesos aprendidos.

**En modo IA vs IA:** los botones están deshabilitados. La batalla ocurre automáticamente con una pausa de 1.5 segundos entre turnos para que puedas seguirla.

Al terminar la batalla, presiona cualquier tecla para ver la pantalla de resultados con el ganador y las estadísticas.

---

## 4. Cómo jugar — Modo Consola

Ejecuta `python3 main.py --console` (Linux) o `python main.py --console` (Windows).

### Menú principal

```
╔══════════════════════════════════════════╗
║            POKEFISI  - Consola           ║
╠══════════════════════════════════════════╣
║  1. Humano vs IA                         ║
║  2. IA vs IA                             ║
║  3. Entrenar Heuristica Avanzada         ║
║  4. Entrenar Heuristica Mejorada         ║
║  5. Entrenar IA Genetica                 ║
║  6. Eliminar pesos entrenados            ║
║  7. Salir                                ║
╚══════════════════════════════════════════╝
Elige una opcion: _
```

Escribe el número y presiona `Enter`.

Las opciones **3**, **4** y **5** lanzan entrenamientos: piden sus parámetros, muestran el progreso en tiempo real y guardan los pesos resultantes automáticamente (ver sección 10). La opción **6** elimina archivos de pesos entrenados.

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
| `K` | Factor de ajuste global, definido en `config.py` como `K = 0.25` |

### ¿Qué hace cada parte?

- **`(Attack / Defense_op) * BasePower`**: el núcleo del daño. Cuanto mayor sea el ataque del atacante y menor la defensa del defensor, más daño. El poder del movimiento amplifica este cociente.
- **`- Speed_op * K`**: la velocidad del defensor reduce el daño, simulando que un Pokémon rápido esquiva parcialmente el golpe. Con K=0.25, un defensor con 100 de velocidad reduce 25 puntos de daño bruto.

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
raw   = (130 / 40) * 120 - 90 * 0.25
      = 3.25 * 120 - 22.5
      = 390 - 22.5
      = 367.5

tipo  = Fighting → Electric  → x1.0 (neutro)

final = int(367.5 * 1.0) = 367 daño
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

La simulación calcula el **daño esperado de forma determinista** (sin tirada de precisión), mediante el método `_sim_damage` de la clase base, para que el razonamiento sea reproducible:

```python
# ai/heuristic_basic.py
def _apply_action(self, state: BattleState, player_id: int, action: dict):
    if action["type"] == "switch":
        state.set_active_index(player_id, action["pokemon_index"])
        return
    move_index = action["move_index"]
    attacker   = state.get_active(player_id)
    defender   = state.get_active(3 - player_id)
    moves      = attacker.get_available_moves()
    if move_index < len(moves):
        defender.take_damage(self._sim_damage(attacker, moves[move_index], defender))
```

`_sim_damage` incorpora la precisión como factor multiplicativo (valor esperado) en lugar de lanzar un dado, por lo que la simulación nunca "falla" al azar y dos evaluaciones del mismo estado dan siempre el mismo resultado. Todos los agentes que simulan (heurísticas, minimax y genético) comparten este mismo daño determinista.

#### ¿Por qué esta heurística es mejor que el agente aleatorio?

El agente aleatorio puede usar un movimiento de tipo Agua contra un Pokémon de tipo Agua (×0.5 de daño, muy ineficiente). La heurística básica **siempre elige el movimiento que cause más daño** porque mayor daño → menor HP del oponente → score más alto.

También considera los cambios de Pokémon: si cambiar a otro Pokémon del equipo resulta en un estado mejor (por ejemplo, sacar un Pokémon que se va a morir y poner uno con más HP), la heurística lo detecta y realiza el cambio.

---

### Agente 3 — Heurística Avanzada (`ai/heuristic_advanced.py`)

Este agente amplía la heurística básica considerando el **equipo completo** en lugar de solo el Pokémon activo. Su función de evaluación combina **cuatro diferenciales** (mi valor − el del rival), todos acotados en `[-1, 1]`, de modo que un estado perfectamente simétrico vale `0`.

#### La función de evaluación de 4 diferenciales

```python
# ai/heuristic_advanced.py
w = self.weights
return (
      w[0] * alive_diff   # diferencia de Pokémon vivos (normalizada)
    + w[1] * hp_diff      # diferencia de HP promedio de los equipos
    + w[2] * type_adv     # mi ventaja de tipo − la del rival
    + w[3] * speed_adv    # ventaja de velocidad del activo
)
```

| Diferencial | Cálculo | ¿Por qué importa? |
|---|---|---|
| `alive_diff` | (vivos_propios − vivos_rivales) / total | Más Pokémon vivos = más opciones tácticas |
| `hp_diff` | HP promedio propio − HP promedio rival | Mide quién está mejor de salud globalmente |
| `type_adv` | (mi mejor multiplicador − el del rival) / 4 | Explotar ventajas de tipo es clave |
| `speed_adv` | (vel_propia − vel_rival) / MAX_SPE | Actuar primero da ventaja táctica |

Los **pesos por defecto** son `[0.40, 0.35, 0.15, 0.10]`. Pueden ajustarse manualmente o, mejor, mediante entrenamiento automático (sección 10). Como cada término es un diferencial, el signo del score indica directamente quién va ganando.

---

### Agente 3b — Heurística Mejorada (`ai/heuristic_improved.py`)

Una variante más rica que evalúa **6 componentes** en lugar de 4, incorporando nociones tácticas adicionales:

| Componente | Idea |
|---|---|
| supervivencia | diferencia de Pokémon vivos |
| HP ponderado | HP del equipo dando más peso al Pokémon activo |
| amenaza de KO | ¿puedo noquear al rival este turno? |
| peligro de KO | ¿el rival puede noquearme a mí? |
| cobertura de equipo | variedad de tipos ofensivos del equipo |
| velocidad | ventaja de velocidad del activo |

Su lógica de decisión es la misma (simula cada acción a 1 ply y elige la de mayor score); solo cambia la función de evaluación.

---

### Agente 4 — Minimax con poda alfa-beta (`ai/minimax_agent.py`)

A diferencia de las heurísticas, que solo miran un turno, el Minimax realiza **búsqueda adversaria**: explora un árbol de jugadas anticipando la respuesta del rival. Usa una formulación *paranoid* con árbol alternante —en los nodos **MAX** el agente maximiza su evaluación y en los nodos **MIN** el rival la minimiza— y, cuando ambas acciones quedan fijadas, simula el turno completo y desciende un nivel de profundidad. Las hojas se valoran con los mismos 4 diferenciales de la Heurística Avanzada; los estados terminales valen `±1`.

```python
# ai/minimax_agent.py  (esquema)
def _minimax(self, state, depth, alpha, beta, player_id, opp_id, my_action):
    if state.is_terminal(): return self._evaluate_terminal(...)
    if depth == 0:          return self._evaluate(...)
    if my_action is None:                      # nodo MAX (yo)
        best = -inf
        for a in self._possible_actions(state, player_id):
            best = max(best, self._minimax(..., my_action=a))
            alpha = max(alpha, best)
            if beta <= alpha and self.prune: break   # poda β
        return best
    else:                                      # nodo MIN (rival)
        best = +inf
        for o in self._possible_actions(state, opp_id):
            sim = state.copy(); self._apply_turn(sim, player_id, my_action, o)
            best = min(best, self._minimax(sim, depth-1, ..., my_action=None))
            beta = min(beta, best)
            if beta <= alpha and self.prune: break   # poda α
        return best
```

La **poda alfa-beta** descarta ramas que no pueden mejorar la decisión, conservando exactamente el mismo resultado que el minimax puro pero explorando muchos menos nodos (en los experimentos del informe, una reducción del 50 % a profundidad 2 y del 82 % a profundidad 3). La profundidad `d` (en turnos) es configurable: `Minimax d=2` y `Minimax d=3` ofrecen distintos equilibrios entre previsión y coste.

---

### Agente 4b — Expectimax contra modelo (`ai/expectimax_agent.py`)

Variante de búsqueda que **no asume el peor caso**. En lugar de minimizar sobre todas las acciones del rival (paranoid), consulta una **política fija** que modela al oponente (por defecto la Heurística Básica) y desciende por la jugada que el rival *realmente* haría, decidida sobre el estado **antes** de ver la nuestra (acorde con la simultaneidad del combate). Reutiliza la evaluación, la simulación de turno y el panel cerebro del Minimax; al colapsar la rama del rival a una sola acción, es más económico. Es un agente **adicional**: no reemplaza al Minimax.

---

### Agente 5 — Genético sobre Minimax (`ai/genetic_agent.py`)

Es exactamente el agente Minimax anterior, pero con los **pesos de su función de evaluación optimizados por un algoritmo genético** (sección 10) en lugar de ajustados a mano. Hereda toda la búsqueda con poda alfa-beta; solo cambian los cuatro pesos. Se carga desde un archivo `data/genetic_*.json` y aparece como `Genetico g=… p=… d=…`.

---

### Agente 6 — Heurística Entrenada (`ai/heuristic_trained.py`)

Es una subclase de `HeuristicAdvancedAgent` que en lugar de usar los pesos por defecto, **carga pesos optimizados** desde un archivo JSON generado por el proceso de entrenamiento por *hill-climbing*.

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
| `copy()` | Hace un **clon ligero** del estado para que la IA simule sin alterar el real |
| `next_alive_index()` | Encuentra el siguiente Pokémon vivo de un equipo |

El método `copy()` es crítico para el rendimiento del Minimax, que clona el estado miles de veces por decisión. En lugar de una costosa `copy.deepcopy()`, hace una **copia superficial de cada Pokémon**: durante una simulación lo único que se muta es el `current_hp` y los índices de activo, mientras que tipos, movimientos y estadísticas son inmutables y se pueden compartir. Este cambio aceleró la búsqueda en torno a un orden de magnitud y volvió viable el algoritmo genético sobre minimax.

```python
# engine/state.py
def copy(self):
    new = BattleState.__new__(BattleState)
    new.player1_team = [_copy.copy(p) for p in self.player1_team]
    new.player2_team = [_copy.copy(p) for p in self.player2_team]
    new.active_index_p1 = self.active_index_p1
    new.active_index_p2 = self.active_index_p2
    new.turn_number = self.turn_number
    return new
```

---

## 10. Entrenamiento de la IA — Hill-Climbing y Algoritmo Genético

PokeFisi ofrece tres entrenamientos. Los dos primeros (opciones 3 y 4 de consola) ajustan los pesos de una heurística por **stochastic hill-climbing**; el tercero (opción 5 de consola o el botón de la GUI) evoluciona los pesos del **Minimax** con un **algoritmo genético**.

### 10.1. Hill-Climbing (Heurística Avanzada y Mejorada)

El entrenamiento busca los pesos que maximizan el win-rate de la heurística enfrentándola contra una mezcla de oponentes. El algoritmo se llama **Stochastic Hill-Climbing** (escalada estocástica de colinas).

#### Idea general

Imagina los pesos (4 en la Heurística Avanzada, 6 en la Mejorada) como una posición en un espacio de varias dimensiones. El objetivo es encontrar el punto de ese espacio donde el agente gana más batallas. Para eso el algoritmo:

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
    supervivencia   0.3821  (base 0.400,  -0.0179)
    hp_diff         0.4103  (base 0.350,  +0.0603)
    tipo            0.1342  (base 0.150,  -0.0158)
    velocidad       0.0734  (base 0.100,  -0.0266)
```

#### Formato del archivo de pesos

El archivo `data/weights_N.json` tiene la siguiente estructura (4 pesos para la Avanzada):

```json
{
  "weights": [0.382, 0.410, 0.134, 0.073],
  "battles": 200,
  "win_rate": 0.74
}
```

El orden de los pesos corresponde siempre a: `[supervivencia, hp_diff, tipo, velocidad]`. La Heurística Mejorada se guarda igual pero con 6 pesos en `data/weights_improved_N.json`.

### 10.2. Algoritmo Genético sobre Minimax

La opción **5** de consola y el botón **ENTRENAR IA GENETICA** de la GUI evolucionan los 4 pesos que usa el **Minimax** en sus hojas. Cada *individuo* es un vector de 4 pesos; su *fitness* es la tasa de victorias de un `Minimax(d, pesos)` en `K` batallas contra un **panel de rivales** (Aleatorio, Básica y Avanzada por defecto), repartidos por igual entre las batallas. Usar un panel en vez de un solo rival reduce el sobreajuste y mejora la generalización (Experimento D del informe). El ciclo combina **selección por torneo**, **cruce uniforme**, **mutación gaussiana** y **elitismo** durante `G` generaciones, y guarda el mejor resultado en `data/genetic_gG_pP_dD.json`. La explicación completa, paso a paso, está en [`docs/algoritmo_genetico.md`](algoritmo_genetico.md).

Desde la **GUI**, el entrenamiento corre en segundo plano con barra de progreso por batalla y una gráfica de fitness por generación, y puede cancelarse; al terminar, el nuevo agente queda seleccionable sin reiniciar.

### Registro automático de agentes (`ai/registry.py`)

Al iniciar el juego (GUI o consola), el registro escanea `data/weights_*.json` y `data/genetic_*.json` y añade automáticamente cada agente entrenado a la lista de selección:

```python
# ai/registry.py
def build_registry():
    # base + heurísticas entrenadas + mejoradas + genéticos encontrados en data/
    return _BASE + _trained_entries() + _improved_trained_entries() + _genetic_entries()
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
    │       ├── random_agent.py      ← Agente Aleatorio
    │       ├── heuristic_basic.py   ← Heurística Básica
    │       ├── heuristic_advanced.py← Heurística Avanzada (4 diferenciales)
    │       ├── heuristic_improved.py← Heurística Mejorada (6 componentes)
    │       ├── heuristic_trained.py ← carga pesos desde weights_*.json
    │       ├── minimax_agent.py     ← Minimax con poda alfa-beta
    │       ├── genetic_agent.py     ← Minimax con pesos evolucionados
    │       ├── genetic_trainer.py   ← algoritmo genético sobre minimax
    │       ├── trainer.py           ← entrenamiento hill-climbing de heurísticas
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
K             = 0.25   # factor de velocidad en la fórmula de daño
FPS           = 60     # cuadros por segundo de la GUI
AI_TURN_DELAY = 1500   # pausa entre turnos en IA vs IA (milisegundos)
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

La batalla termina cuando **todos** los Pokémon de un equipo tienen 0 HP. Además, para evitar batallas infinitas (por ejemplo Normal vs Ghost, que no se pueden hacer daño mutuo, o agentes que solo cambian), existe un tope de `MAX_TURNS = 200` turnos en `engine/battle.py`; si se alcanza, el ganador se decide por número de Pokémon vivos y, en caso de empate, por HP total.

### Diagrama simplificado

```
Battle.run()
    └─ while not is_terminal() and turno < MAX_TURNS:
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

### Para ganar al Minimax y al Genético

Estos agentes anticipan tu respuesta varios turnos, así que las trampas de "un solo turno" no funcionan tan bien. Aun así:

- **El Minimax es pesimista** (asume que jugarás siempre lo peor para él): a veces hace cambios demasiado defensivos. Un equipo agresivo y rápido puede castigar esa cautela.
- **Razona sobre el daño determinista** (sin azar): los movimientos de baja precisión pero alto poder pueden sorprenderlo cuando aciertan.
- Contra el **Genético**, observa en el panel cerebro sus pesos aprendidos: si valora mucho la velocidad, prioriza tú Pokémon rápidos; si prioriza el HP, un planteamiento de desgaste le cuesta más.

### Para ganar a un agente entrenado

Depende de cómo resultaron sus pesos. Observa los pesos en la pantalla de selección o en el panel cerebro:

- Si **tipo** es alto, el agente prioriza la ventaja de tipo: construye un equipo con cobertura de tipos variada.
- Si **velocidad** es alta, valora mucho actuar primero: usa Pokémon de alta velocidad.
- Si **hp_diff** domina, juega al desgaste con Pokémon defensivos y de mucho HP.

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

## 14. El panel cerebro — cómo leer el razonamiento de la IA

El **panel cerebro** (la caja oscura que aparece en la columna derecha del campo cuando un jugador es controlado por una IA) muestra **en tiempo real qué está "pensando" el agente** en el turno actual. No es decoración: refleja exactamente las acciones que el agente evaluó y la puntuación que le dio a cada una. Entenderlo permite verificar que la IA decide como esperamos y explicar su comportamiento.

### 14.1. Arquitectura: dos capas desacopladas

El panel funciona en **dos capas independientes** que se comunican por un único atributo, `last_brain_data`:

1. **El agente calcula y guarda su razonamiento.** Cada agente, dentro de su `choose_action`, evalúa todas las acciones posibles y deja el resultado en `self.last_brain_data` (un diccionario). No dibuja nada.
2. **La GUI dibuja lo que el agente dejó.** El método `_draw_brain_panel` de `gui/screens/battle_screen.py` lee `agent.last_brain_data` y lo pinta. No recalcula nada.

```python
# gui/screens/battle_screen.py  (método _draw_brain_panel)
data = getattr(agent, "last_brain_data", None)
if data is None:
    # aún no ha jugado: "Esperando primer turno..."
    ...
for ev in data["evaluations"]:      # una fila por acción evaluada
    # nombre, barra de daño, "XHP rival:Y%", score, y resaltado si fue la elegida
    ...
```

La gran ventaja de este diseño: **el mismo panel sirve para los 6 agentes**. Cada uno rellena su propio diccionario con su fórmula y, si tiene datos extra (componentes, nodos, pesos), el panel los muestra automáticamente al pie.

### 14.2. Anatomía del diccionario `last_brain_data`

| Clave | Contenido | Qué agentes la rellenan |
|---|---|---|
| `formula` | Texto de la fórmula de evaluación que se muestra bajo el nombre del agente | Todos |
| `evaluations` | Lista con una entrada por acción posible (ver abajo) | Todos |
| `components` *(dentro de cada evaluación)* | Desglose por componente de la acción elegida | Heurística Avanzada y Mejorada |
| `stats` | `nodos`, `podas`, `depth`, `ms` de la búsqueda | Minimax y Genético |
| `pv` | Variante principal: mi mejor acción → mejor réplica del rival | Minimax y Genético |
| `weights` | Pesos aprendidos frente a los de base | Genético |

Cada elemento de `evaluations` es un diccionario con estos campos:

| Campo | Significado |
|---|---|
| `name` | Nombre de la acción: el movimiento (`Fire Blast`) o el cambio (`-> Gengar`) |
| `damage` | Daño inmediato que haría ese movimiento (0 en los cambios) |
| `opp_hp_after` | HP del rival tras recibir ese daño |
| `opp_max_hp` | HP máximo del rival (para calcular el porcentaje y la barra) |
| `score` | Puntuación que la función de evaluación asigna a la acción |
| `chosen` | `True` solo en la acción finalmente elegida (la marcada con `*`) |

### 14.3. Cómo leer cada fila

Cada fila del panel representa **una acción evaluada** y muestra cuatro cosas:

```
* -> Magmar            ▮▯▯▯▯▯▯▯   0 HP  rival:100%        -0.45
└─ acción (chosen=*)   └ barra    └ daño y % HP rival     └ score
```

| Elemento visual | De dónde sale | Cómo interpretarlo |
|---|---|---|
| Nombre + `*` + resaltado | `name`, `chosen` | El `*` y el fondo azul marcan la acción elegida (la de mayor `score`) |
| Barra roja | `damage / opp_max_hp` | Proporción de daño del golpe respecto al HP rival |
| `147HP rival:51%` | `damage`, `opp_hp_after` | Daño infligido y HP que le quedaría al rival (verde >50 %, amarillo 25-50 %, rojo <25 %) |
| `+0.02` / `-1.00` | `score` | Valor de la acción para el agente (verde si ≥ 0, rojo si < 0) |

> **Distinción clave — barra ≠ score.** La barra y el texto `XHP rival:Y%` son el **daño inmediato** del movimiento. El número de la derecha es el **valor de la evaluación**, que en el Minimax/Genético es el resultado de mirar varios turnos hacia delante. Por eso una acción puede hacer poco daño inmediato pero tener mejor score (o al revés). En las capturas de ejemplo, todos los ataques de Pikachu contra Snorlax valían `-0.47`, pero **cambiar a Magmar** (`-0.45`) era la opción menos mala, así que el Genético cambió de Pokémon en lugar de atacar.

### 14.4. Datos extra del Minimax y el Genético

Cuando el agente es de búsqueda, debajo de las filas aparecen líneas adicionales:

```
nodos:3182  podas a-b:689  d=3  40ms
yo: Magmar  ->  rival: Hyper Beam
pesos: superv 0.24  hp 0.47  tipo 0.29  vel 0.01
```

| Línea | Origen | Significado |
|---|---|---|
| `nodos:3182` | `stats["nodos"]` | Estados del árbol explorados en esta decisión |
| `podas a-b:689` | `stats["podas"]` | Ramas cortadas por la poda alfa-beta (cuantas más, más ahorro) |
| `d=3  40ms` | `stats["depth"]`, `stats["ms"]` | Profundidad de búsqueda y tiempo de cómputo |
| `yo: … -> rival: …` | `pv` (`_principal_variation`) | La **variante principal**: la mejor jugada propia y la mejor réplica que el agente anticipa del rival |
| `pesos: …` | `weights` | Los pesos **evolucionados** de la evaluación (solo el Genético) |

La variante principal la calcula el método `_principal_variation` de `ai/minimax_agent.py`, que tras fijar la mejor acción propia busca la respuesta del rival que minimiza la evaluación. Es la forma de "ver" qué intercambio está anticipando el agente.

### 14.5. Dónde se genera el panel, agente por agente

| Agente | Archivo donde rellena `last_brain_data` | Extras que añade |
|---|---|---|
| Heurística Básica | `ai/heuristic_basic.py` | `formula = "score = HP_propio% - HP_rival%"` |
| Heurística Avanzada | `ai/heuristic_advanced.py` | fórmula de 4 pesos + `components` |
| Heurística Mejorada | `ai/heuristic_improved.py` | fórmula de 6 componentes + `components` |
| Minimax | `ai/minimax_agent.py` | `stats` (nodos, podas, ms) + `pv` |
| Genético | `ai/genetic_agent.py` | lo del Minimax + `weights` |
| Expectimax | `ai/expectimax_agent.py` | `formula` indicando el modelo de rival usado |

El Agente Aleatorio no rellena el panel (no evalúa nada), por lo que se muestra `Esperando primer turno...` mientras no haya datos.

---

## 15. Comandos del juego y funciones que los implementan

Esta sección mapea **cada acción que realiza el jugador** con la función y el archivo que la hacen posible. Sirve como referencia rápida para localizar el código detrás de cada elemento de la interfaz.

### 15.1. Las acciones del jugador

En cualquier turno, un jugador solo puede hacer dos cosas, y ambas se representan siempre con el mismo formato de diccionario:

```python
{"type": "move",   "move_index": 0-3}   # atacar con uno de los 4 movimientos
{"type": "switch", "pokemon_index": 0-N} # cambiar al Pokémon de esa posición
```

Este es el "lenguaje" común que entienden el motor (`engine/battle.py`) y todos los agentes (`ai/`). Tanto un humano haciendo clic como una IA razonando acaban produciendo uno de estos dos diccionarios.

La lista de acciones legales en un momento dado la genera `_possible_actions` en `ai/base_agent.py`: añade un `move` por cada movimiento disponible del Pokémon activo y un `switch` por cada Pokémon vivo del banco que no sea el activo.

### 15.2. Comandos en la GUI (modo Humano vs IA)

| Comando en pantalla | Cómo se activa | Función / clase que lo implementa | Acción que produce |
|---|---|---|---|
| Botón de movimiento (`Aqua Tail`, etc.) | Clic en la tarjeta del ataque | clase `MoveButton` en `gui/screens/battle_screen.py` | `{"type": "move", "move_index": i}` |
| Botón **CAMBIAR POKEMON** | Clic en el botón morado bajo los movimientos | clase `SwitchButton` → abre el selector | inicia `_try_switch()` |
| Selector "¿A qué Pokémon cambiar?" | Clic en el Pokémon deseado | `_draw_switch_picker` + `_handle_picker_event` | `{"type": "switch", "pokemon_index": idx}` |

Cada tarjeta de movimiento muestra tres datos del objeto `Move`: el **tipo** (badge de color), el **Poder Base** (`BP`) y la **Precisión** (`Acc`). Son los mismos campos descritos en la [sección 6](#6-los-movimientos-y-sus-estadísticas).

### 15.3. Comandos en la GUI (modo IA vs IA)

| Comando | Cómo se activa | Efecto |
|---|---|---|
| **PAUSAR / REANUDAR** | Clic en el botón o tecla `Espacio` | Detiene o reanuda el avance automático de turnos |

En este modo los botones de acción están deshabilitados: las decisiones las toman los agentes y solo se observa la batalla (con la pausa de `AI_TURN_DELAY` ms entre turnos definida en `config.py`).

### 15.4. Comandos en el modo Consola

Durante la batalla por consola, cada acción es un número que se escribe y se confirma con `Enter`. Los números `1-4` corresponden a los movimientos y el siguiente a cambiar de Pokémon; la lectura y validación se hacen en `console/console_battle.py`, que traduce el número al mismo diccionario `{"type": ...}`.

### 15.5. Mapa rápido de funciones clave

| Quiero entender… | Función | Archivo |
|---|---|---|
| Qué estadísticas reales tiene un Pokémon (nivel 100) | `battle_stats()` + constructor de `Pokemon` | `engine/pokemon.py` |
| Cómo se calcula el daño de un golpe | `calculate_damage()` | `engine/damage.py` |
| Cómo se resuelven las ventajas de tipo | `get_type_multiplier()` + `TYPE_CHART` | `engine/damage.py` |
| Qué acciones puede tomar un agente | `_possible_actions()` | `ai/base_agent.py` |
| Cómo decide una heurística | `choose_action()` + `_evaluate()` | `ai/heuristic_*.py` |
| Cómo razona la búsqueda adversaria | `_minimax()`, `_evaluate()`, `_principal_variation()` | `ai/minimax_agent.py` |
| Cómo se ejecuta un turno completo | `step()` | `engine/battle.py` |
| Cómo se dibuja el razonamiento de la IA | `_draw_brain_panel()` | `gui/screens/battle_screen.py` |

> Para el detalle de un turno (orden por velocidad, ejecución y reemplazo automático) consulta la [sección 12](#12-flujo-completo-de-una-batalla); para la lógica interna de cada agente, la [sección 9](#9-inteligencia-artificial--los-agentes).

---

*Manual de PokeFisi — Proyecto académico de Inteligencia Artificial*
