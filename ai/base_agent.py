from abc import ABC, abstractmethod
from engine.state import BattleState
from engine.damage import get_type_multiplier
from config import K


class Agent(ABC):
    def __init__(self, name: str = "Agent"):
        self.name = name
        self.wins = 0
        self.battles = 0

    @abstractmethod
    def choose_action(self, state: BattleState, player_id: int) -> dict:
        """
        Retorna un dict:
            {"type": "move",   "move_index": 0-3}
          o {"type": "switch", "pokemon_index": 0-N}
        """

    def get_info_lines(self) -> list[str]:
        return []

    def on_battle_end(self, won: bool):
        self.battles += 1
        if won:
            self.wins += 1

    def win_rate(self) -> float:
        return self.wins / self.battles if self.battles > 0 else 0.0

    @staticmethod
    def _sim_damage(attacker, move, defender) -> int:
        """Daño esperado determinista para simulaciones internas (sin tirada de precisión)."""
        raw = (attacker.attack / max(1, defender.defense)) * move.base_power - defender.speed * K
        raw = max(1, raw)
        mult = get_type_multiplier(move.type, defender.types)
        return max(0, int(raw * mult * move.accuracy / 100))

    def _possible_actions(self, state: BattleState, player_id: int) -> list[dict]:
        actions = []
        active = state.get_active(player_id)
        for i in range(len(active.get_available_moves())):
            actions.append({"type": "move", "move_index": i})
        for i, p in enumerate(state.get_team(player_id)):
            if p.is_alive() and i != state.get_active_index(player_id):
                actions.append({"type": "switch", "pokemon_index": i})
        return actions if actions else [{"type": "move", "move_index": 0}]
