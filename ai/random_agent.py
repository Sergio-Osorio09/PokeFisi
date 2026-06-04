import random
from ai.base_agent import Agent
from engine.state import BattleState


class RandomAgent(Agent):
    def __init__(self):
        super().__init__("Agente Aleatorio")
        self.last_brain_data = None

    def get_info_lines(self) -> list[str]:
        return ["Elige accion al azar en cada turno."]

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        actions = self._possible_actions(state, player_id)
        choice  = random.choice(actions)

        # Panel "cerebro": no evalua nada, todas las acciones son equiprobables.
        me  = state.get_active(player_id)
        opp = state.get_active(3 - player_id)
        prob = 1.0 / len(actions)
        evals = []
        for action in actions:
            if action["type"] == "move":
                moves  = me.get_available_moves()
                move   = moves[action["move_index"]]
                damage = self._sim_damage(me, move, opp)
                label  = move.name
            else:
                team   = state.get_team(player_id)
                damage = 0
                label  = f"-> {team[action['pokemon_index']].name}"
            evals.append({
                "name":         label,
                "damage":       damage,
                "opp_hp_after": max(0, opp.current_hp - damage),
                "opp_max_hp":   opp.max_hp,
                "my_hp_ratio":  me.hp_ratio(),
                "score":        prob,
                "chosen":       action == choice,
            })

        self.last_brain_data = {
            "formula":     f"eleccion uniforme: cada accion = 1/{len(actions)}",
            "evaluations": evals,
        }
        return choice
