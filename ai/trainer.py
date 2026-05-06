import random
import math
import json
import os

from engine.loader import load_moves, build_team
from engine.state import BattleState
from engine.battle import Battle
from ai.heuristic_advanced import HeuristicAdvancedAgent, DEFAULT_WEIGHTS
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent

_ALL_MOVES = None


def _get_moves():
    global _ALL_MOVES
    if _ALL_MOVES is None:
        _ALL_MOVES = load_moves()
    return _ALL_MOVES


def _play_one(weights: list[float], battle_index: int) -> bool:
    all_moves = _get_moves()
    ids1 = random.sample(range(1, 31), 3)
    ids2 = random.sample(range(1, 31), 3)
    team1 = build_team(ids1, all_moves)
    team2 = build_team(ids2, all_moves)
    state = BattleState(team1, team2)
    our_agent = HeuristicAdvancedAgent(weights)
    opp = RandomAgent() if battle_index % 2 == 0 else HeuristicBasicAgent()
    battle = Battle(state, our_agent, opp)
    battle.run()
    return state.get_winner() == 1


def run_training(n_battles: int) -> dict:
    current_w = DEFAULT_WEIGHTS[:]
    best_w = DEFAULT_WEIGHTS[:]

    wins = 0
    window: list[int] = []
    best_wr = 0.0
    report_every = max(1, n_battles // 10)
    width = len(str(n_battles))

    print(f"\n  Entrenando {n_battles} batallas vs Random (50%) y HeuristicBasica (50%)...\n")

    for i in range(n_battles):
        # Temperatura: 0.12 → ~0.005 con decaimiento exponencial
        t = 0.12 * math.exp(-3.5 * i / n_battles)

        # Generar pesos candidatos perturbando los actuales
        candidate = [max(0.005, w + random.gauss(0, t)) for w in current_w]
        total = sum(candidate)
        candidate = [w / total for w in candidate]

        won = _play_one(candidate, i)

        if won:
            current_w = candidate
            wins += 1

        window.append(1 if won else 0)
        if len(window) > 20:
            window.pop(0)

        wr_window = sum(window) / len(window)
        if wr_window >= best_wr and len(window) >= 10:
            best_wr = wr_window
            best_w = current_w[:]

        if (i + 1) % report_every == 0:
            pct = (i + 1) * 100 // n_battles
            total_wr = wins / (i + 1)
            print(f"  [{pct:3d}%] Batalla {i+1:>{width}}/{n_battles}"
                  f"  |  Win-rate: {total_wr:.1%}"
                  f"  |  Temp: {t:.4f}")

    return {
        "weights": best_w,
        "battles": n_battles,
        "win_rate": wins / n_battles,
    }


def save_weights(data: dict) -> str:
    n = data["battles"]
    path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'data', f'weights_{n}.json')
    )
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    return path
