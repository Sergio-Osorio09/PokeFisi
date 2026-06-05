# Agente Aleatorio — La Línea Base

## ¿Qué es un Agente Aleatorio?

El **Agente Aleatorio** es la IA más simple posible: en cada turno elige una acción completamente al azar, sin importar el estado de la batalla. No evalúa nada, no aprende, no razona.

Su utilidad no es ganar batallas — es servir de **referencia mínima**. Cualquier IA que no supere al agente aleatorio no está haciendo nada útil.

> Si una IA gana más del 50% de las batallas contra el agente aleatorio, significa que su estrategia tiene algún valor real. Si gana menos, algo está mal.

---

## El problema que resuelve en PokeFisi

No resuelve ningún problema de estrategia. Su función es ser el **punto de partida de comparación** para medir qué tan buenas son las demás IAs.

También se usa durante el entrenamiento de la `HeuristicaEntrenada`: el 50% de las batallas de entrenamiento son contra el agente aleatorio para asegurar que los pesos aprendidos funcionan incluso contra oponentes impredecibles.

---

## Cómo funciona paso a paso

### Turno a turno

```
1. Obtener lista de acciones posibles:
   - Movimientos disponibles del Pokémon activo (max. 4)
   - Cambios de Pokémon (todos los vivos que no sean el activo)

2. Elegir una al azar con igual probabilidad.

3. Ejecutar la acción elegida.
```

No hay simulación, no hay evaluación, no hay memoria del turno anterior. Cada decisión es independiente de todas las demás.

### Ejemplo concreto

```
Estado: Charizard activo, 3 movimientos disponibles, 1 cambio posible

Acciones posibles:
  [0] Movimiento: Fire Blast
  [1] Movimiento: Air Slash
  [2] Movimiento: Flamethrower
  [3] Cambio: → Blastoise

Dado virtual: sale 2

Acción elegida: Flamethrower
```

El próximo turno vuelve a tirar el dado. No importa si Flamethrower funcionó o no.

---

## Código completo

La decisión es una sola línea: `_possible_actions` devuelve la lista de acciones válidas y `random.choice` selecciona una uniformemente.

```python
class RandomAgent(Agent):
    def choose_action(self, state, player_id):
        actions = self._possible_actions(state, player_id)
        choice  = random.choice(actions)
        # ... además rellena last_brain_data con barras uniformes (1/N)
        #     para el panel cerebro de la GUI ...
        return choice
```

El resto del método solo construye los datos del **panel cerebro** (todas las acciones con probabilidad `1/N` y la elegida marcada), de modo que en la GUI se vea claramente que el agente elige al azar. Esa información no influye en la decisión.

---

## Por qué es útil estudiar este agente

### 1. Define el piso de rendimiento

Un agente estratégico debería ganar cómodamente contra el aleatorio. En PokeFisi, se espera que:

| Agente | Win-rate vs Aleatorio (esperado) |
|---|---|
| Aleatorio | ~50% |
| Heurística Básica | ~65–75% |
| Heurística Avanzada | ~75–85% |
| Minimax d=2 | ~65–75% |
| Minimax d=3 | ~70–80% |

> Rangos orientativos. En los experimentos del informe ([`docs/informe/`](informe/)) el Minimax *paranoid* no siempre domina a las heurísticas, porque asume que el rival juega de forma óptima contra él y razona sobre un modelo de daño determinista; con profundidad mayor mejora.

### 2. Expone la varianza del juego

Las batallas Pokémon tienen mucha aleatoriedad (equipos distintos, tipos variados). El aleatorio la explota al máximo: a veces elegirá exactamente el movimiento correcto por casualidad. Esto nos recuerda que ningún agente puede ganar el 100% de las batallas.

### 3. Referencia para detectar bugs

Si una IA pierde más del 50% contra el aleatorio, hay un bug en su implementación. El aleatorio es el "detector de errores" más simple.

---

## Limitaciones obvias

- **No tiene ventaja de tipo**: puede usar un movimiento que no hace daño (x0.0) sin saberlo.
- **No evita el suicidio**: puede cambiar a un Pokémon débil contra el oponente activo.
- **No capitaliza victorias**: si puede noquear al rival de un golpe, podría no elegir ese movimiento.
- **No recuerda nada**: cada turno empieza desde cero.

---

## Comparación con los demás agentes

| Característica | Aleatorio | Básica | Avanzada | Minimax |
|---|---|---|---|---|
| Evalúa opciones | No | Sí | Sí | Sí |
| Mira el futuro | No | 1 turno | 1 turno | N turnos |
| Usa tipos | No | No | Sí | Sí |
| Aprende | No | No | No | No |
| Velocidad | Instantáneo | Muy rápido | Rápido | Lento |
