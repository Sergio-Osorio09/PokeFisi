# Modo Torneo y banco de pruebas de IAs

PokeFisi incluye un sistema para **comparar, clasificar y documentar** a todas las IAs, en dos formas: un **modo Torneo** en la GUI y un **banco de experimentos headless**.

## Reglas comunes

- **Mejor de 3** por enfrentamiento (la primera IA en ganar 2 batallas avanza).
- **Equipos aleatorios 3v3** en cada batalla → equilibra los combates y evita el sesgo de un equipo fijo.
- **Pokémon excluidos por desbalanceados** (`arena/core.EXCLUDED_POKEMON`): **Mewtwo, Dragonite, Cloyster, Snorlax**. Son los outliers de stats bajo la fórmula de daño `(Atk/Def)·BP − Spe·K`, donde **defensa** (denominador) y **velocidad** (mueve primero + recibe menos) altas son especialmente fuertes.
- Las IAs salen del **registro** (`ai/registry.py`): Aleatorio, Heurísticas, Minimax, Expectimax y Genéticos entrenados.

## Modo Torneo (GUI)

Botón **TORNEO DE IAS** en el menú principal:

1. En `gui/screens/tournament_select.py` eliges **qué IAs participan y cuántas de cada una** (se permiten duplicadas, p. ej. dos `Aleatorio`).
2. El total de competidores debe ser **potencia de 2** (2, 4 u 8).
3. `gui/screens/tournament_screen.py` ejecuta la eliminatoria y muestra el **bracket** llenándose ronda a ronda hasta coronar al **campeón**.
4. Al terminar guarda el reporte en `results/`.

## Experimentos headless

```bash
python run_arena.py 50      # 50 batallas por par (por defecto 30)
```

Corre dos cosas y guarda reportes **JSON + Markdown** en `results/`:

1. **Round-robin** (todos contra todos): `results/round_robin_<fecha>.{json,md}`.
2. **Torneo** eliminatorio con la mayor potencia de 2 que quepa: `results/torneo_<fecha>.{json,md}`.

> Por defecto **excluye las IAs de profundidad 3** (lentas); edita `EXCLUDE_SUBSTR` en `run_arena.py` para incluirlas. Los reportes de `results/` **no se versionan** (son evidencia local generada).

## Métricas que mide

| Métrica | Qué responde |
|---|---|
| **Win-rate** + **IC de Wilson** | % de victorias con su intervalo de confianza (`core.wilson`) |
| **Clasificación** (leaderboard) | ranking de mejor a peor IA |
| **Matriz head-to-head** | cada IA vs cada IA (quién le gana a quién) |
| **Turnos por batalla** | qué tan rápido resuelve los combates |
| **Margen de victoria** | fuerza de equipo restante al ganar (`core.team_strength`) → contundencia |
| **ms por jugada** | costo computacional de decidir (`core.benchmark_decision_ms`) |

## Arquitectura

```
arena/
├── core.py     # team_strength, random_teams, wilson, play_battle, play_match,
│               # round_robin, run_bracket, benchmark_decision_ms, EXCLUDED_POKEMON
└── report.py   # save_round_robin / save_bracket  → JSON + Markdown en results/

run_arena.py    # CLI: round-robin + torneo headless
gui/screens/
├── tournament_select.py   # selección de IAs participantes
└── tournament_screen.py   # bracket animado del torneo
```
