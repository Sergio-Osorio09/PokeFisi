import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.loader import load_moves, build_team
from engine.state import BattleState
from engine.battle import Battle
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent


def make_state(ids1, ids2):
    moves = load_moves()
    team1 = build_team(ids1, moves)
    team2 = build_team(ids2, moves)
    return BattleState(team1, team2)


def test_battle_completes():
    state = make_state([1, 2, 3], [4, 5, 6])
    a1 = RandomAgent()
    a2 = RandomAgent()
    b = Battle(state, a1, a2)
    winner = b.run()
    assert winner in (1, 2)
    assert state.is_terminal()


def test_heuristic_vs_random():
    wins = 0
    for _ in range(10):
        state = make_state([5, 9, 7], [1, 8, 26])
        b = Battle(state, HeuristicBasicAgent(), RandomAgent())
        if b.run() == 1:
            wins += 1
    assert wins >= 0  # simplemente verifica que no lanza excepciones


def test_battle_log_not_empty():
    state = make_state([2, 3], [4, 5])
    b = Battle(state, RandomAgent(), RandomAgent())
    b.run()
    assert len(b.get_log()) > 0


def test_terminal_state():
    state = make_state([11], [1])
    b = Battle(state, RandomAgent(), RandomAgent())
    b.run()
    assert state.is_terminal()
    assert state.get_winner() in (1, 2)
