"""
Heurística Mejorada — 6 componentes con detección de KO y cobertura de equipo.

score = w0*superv  +  w1*hp_pond  +  w2*ko_threat
      + w3*ko_danger  +  w4*cobertura  +  w5*vel
"""
import json
import os
from ai.base_agent import Agent
from engine.state import BattleState
from engine.damage import get_type_multiplier

DEFAULT_WEIGHTS = [0.25, 0.20, 0.20, 0.15, 0.10, 0.10]
_LABELS_SHORT   = ["sv", "hp", "ko+", "ko-", "cob", "vel"]
_LABELS_FULL    = ["superv.", "hp_pond.", "ko_threat", "ko_danger", "cobertura", "velocidad"]
MAX_SPEED       = 130


class HeuristicImprovedAgent(Agent):

    _LABELS = _LABELS_SHORT

    def __init__(self, weights: list[float] | None = None):
        super().__init__("Heurística Mejorada")
        self.weights         = weights if weights is not None else DEFAULT_WEIGHTS[:]
        self.last_brain_data = None

    def get_info_lines(self) -> list[str]:
        w     = self.weights
        w_str = "  ".join(f"{l}:{w[i]:.2f}" for i, l in enumerate(_LABELS_SHORT))
        return [
            "6 componentes: supervivencia, HP pond., KO-threat, KO-danger, cobertura, vel.",
            f"Pesos: {w_str}",
        ]

    def get_visual_stats(self) -> list[tuple]:
        return [
            ("KO Threat",   4, 4, "Detecta noqueos"),
            ("Cobertura",   4, 4, "Equipo completo"),
            ("Componentes", 4, 4, "6 pesos"),
        ]

    # ── Evaluación por componentes ────────────────────────────────────────────

    def _evaluate_components(self, state: BattleState, player_id: int) -> dict:
        opp_id   = 3 - player_id
        my_team  = state.get_team(player_id)
        opp_team = state.get_team(opp_id)
        total    = len(my_team)
        me       = state.get_active(player_id)
        opp      = state.get_active(opp_id)

        # w0 — supervivencia: diferencial de Pokémon vivos [-1, 1]
        superv = (sum(1 for p in my_team  if p.is_alive()) -
                  sum(1 for p in opp_team if p.is_alive())) / total

        # w1 — HP ponderado: 70% activo + 30% promedio equipo [-1, 1]
        hp_active = me.hp_ratio() - opp.hp_ratio()
        hp_team   = (sum(p.hp_ratio() for p in my_team)  / total -
                     sum(p.hp_ratio() for p in opp_team) / total)
        hp_pond   = 0.7 * hp_active + 0.3 * hp_team

        # w2 — ko_threat: fracción del HP rival que puedo quitar [0, 1]
        max_my_dmg = max(
            (self._sim_damage(me, mv, opp) for mv in me.get_available_moves()),
            default=0,
        )
        ko_threat = min(1.0, max_my_dmg / max(1, opp.current_hp))

        # w3 — ko_danger: negativo según cuánto daño puede hacerme el rival [-1, 0]
        max_opp_dmg = max(
            (self._sim_damage(opp, mv, me) for mv in opp.get_available_moves()),
            default=0,
        )
        raw_danger   = min(1.0, max_opp_dmg / max(1, me.current_hp))
        speed_factor = 0.5 if me.speed > opp.speed else 1.0   # si soy más rápido, menor peligro
        ko_danger    = -raw_danger * speed_factor

        # w4 — cobertura del equipo completo [-1, 1]
        my_alive  = [p for p in my_team  if p.is_alive()]
        opp_alive = [p for p in opp_team if p.is_alive()]

        def _cov(attackers, defenders):
            if not attackers or not defenders:
                return 0.0
            total_c = 0.0
            for att in attackers:
                best = 0.0
                for dfd in defenders:
                    for mv in att.get_available_moves():
                        m = get_type_multiplier(mv.type, dfd.types)
                        if m > best:
                            best = m
                total_c += best
            return (total_c / len(attackers)) / 4.0

        cobertura = _cov(my_alive, opp_alive) - _cov(opp_alive, my_alive)

        # w5 — velocidad del activo [-1, 1]
        vel = (me.speed - opp.speed) / MAX_SPEED

        w = self.weights
        return {
            "sv":  w[0] * superv,
            "hp":  w[1] * hp_pond,
            "ko+": w[2] * ko_threat,
            "ko-": w[3] * ko_danger,
            "cob": w[4] * cobertura,
            "vel": w[5] * vel,
        }

    def _evaluate(self, state: BattleState, player_id: int) -> float:
        return sum(self._evaluate_components(state, player_id).values())

    # ── Decisión ─────────────────────────────────────────────────────────────

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        best_score  = float("-inf")
        best_action = None
        best_idx    = 0
        evaluations = []

        me  = state.get_active(player_id)
        opp = state.get_active(3 - player_id)

        for action in self._possible_actions(state, player_id):
            sim     = state.copy()
            self._apply_action(sim, player_id, action)
            score   = self._evaluate(sim, player_id)
            comps   = self._evaluate_components(sim, player_id)
            sim_opp = sim.get_active(3 - player_id)
            damage  = max(0, opp.current_hp - sim_opp.current_hp)

            if action["type"] == "move":
                label = me.get_available_moves()[action["move_index"]].name
            else:
                label = f"-> {state.get_team(player_id)[action['pokemon_index']].name}"

            evaluations.append({
                "name":         label,
                "damage":       damage,
                "opp_hp_after": sim_opp.current_hp,
                "opp_max_hp":   opp.max_hp,
                "score":        score,
                "components":   comps,
                "chosen":       False,
            })

            if score > best_score:
                best_score  = score
                best_action = action
                best_idx    = len(evaluations) - 1

        if evaluations:
            evaluations[best_idx]["chosen"] = True

        w = self.weights
        self.last_brain_data = {
            "formula":     "  ".join(f"{_LABELS_SHORT[i]}:{w[i]:.2f}" for i in range(len(w))),
            "evaluations": evaluations,
        }
        return best_action

    def _apply_action(self, state: BattleState, player_id: int, action: dict):
        if action["type"] == "switch":
            state.set_active_index(player_id, action["pokemon_index"])
            return
        attacker = state.get_active(player_id)
        defender = state.get_active(3 - player_id)
        moves    = attacker.get_available_moves()
        mi       = action["move_index"]
        if mi < len(moves):
            defender.take_damage(self._sim_damage(attacker, moves[mi], defender))


# ── Variante entrenada ────────────────────────────────────────────────────────

class HeuristicImprovedTrainedAgent(HeuristicImprovedAgent):
    def __init__(self, weights_file: str):
        with open(weights_file, encoding="utf-8") as f:
            data = json.load(f)
        super().__init__(weights=data["weights"])
        self.name               = f"H.Mejorada-{data['battles']}"
        self.battles_trained    = data["battles"]
        self.win_rate_training  = data.get("win_rate", 0.0)

    def get_info_lines(self) -> list[str]:
        w     = self.weights
        w_str = "  ".join(f"{l}:{w[i]:.2f}" for i, l in enumerate(_LABELS_SHORT))
        return [
            f"Entrenada: {self.battles_trained} batallas | WR: {self.win_rate_training:.1%}",
            f"Pesos: {w_str}",
        ]


# ── I/O ───────────────────────────────────────────────────────────────────────

def find_improved_weights():
    data_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    if not os.path.isdir(data_dir):
        return
    for fname in sorted(os.listdir(data_dir)):
        if fname.startswith("weights_improved_") and fname.endswith(".json"):
            yield os.path.join(data_dir, fname)
