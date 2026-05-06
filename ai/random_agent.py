import random
from ai.base_agent import Agent
from engine.state import BattleState


class RandomAgent(Agent):
    def __init__(self):
        super().__init__("Agente Aleatorio")

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        return random.choice(self._possible_actions(state, player_id))
