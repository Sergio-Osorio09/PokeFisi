from ai.base_agent import Agent
from engine.state import BattleState


class HeuristicBasicAgent(Agent):
    def __init__(self):
        super().__init__("Heurística Básica")
        self.last_brain_data = None

    def get_info_lines(self) -> list[str]:
        return ["Evalua: hp_propio - hp_oponente del activo."]

    def _evaluate(self, state: BattleState, player_id: int) -> float:
        me = state.get_active(player_id)
        opp = state.get_active(3 - player_id)
        return me.hp_ratio() - opp.hp_ratio()

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        best_score = float("-inf")
        best_action = None
        best_idx   = 0
        evaluations = []

        me  = state.get_active(player_id)
        opp = state.get_active(3 - player_id)

        for action in self._possible_actions(state, player_id):
            sim = state.copy()
            self._apply_action(sim, player_id, action)
            score    = self._evaluate(sim, player_id)
            sim_opp  = sim.get_active(3 - player_id)
            damage   = max(0, opp.current_hp - sim_opp.current_hp)

            if action["type"] == "move":
                moves = me.get_available_moves()
                label = moves[action["move_index"]].name
            else:
                team  = state.get_team(player_id)
                label = f"-> {team[action['pokemon_index']].name}"

            evaluations.append({
                "name":        label,
                "damage":      damage,
                "opp_hp_after": sim_opp.current_hp,
                "opp_max_hp":  opp.max_hp,
                "my_hp_ratio": me.hp_ratio(),
                "score":       score,
                "chosen":      False,
            })

            if score > best_score:
                best_score = score
                best_action = action
                best_idx   = len(evaluations) - 1

        if evaluations:
            evaluations[best_idx]["chosen"] = True

        self.last_brain_data = {
            "formula":     "score = HP_propio% - HP_rival%",
            "evaluations": evaluations,
        }
        return best_action

    def _apply_action(self, state: BattleState, player_id: int, action: dict):
        if action["type"] == "switch":
            state.set_active_index(player_id, action["pokemon_index"])
            return
        move_index = action["move_index"]
        attacker = state.get_active(player_id)
        defender = state.get_active(3 - player_id)
        moves = attacker.get_available_moves()
        if move_index < len(moves):
            defender.take_damage(self._sim_damage(attacker, moves[move_index], defender))
