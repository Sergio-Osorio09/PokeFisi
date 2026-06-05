"""
Agente Expectimax-contra-modelo.

Variante de búsqueda adversaria que NO asume el peor caso (paranoid), sino que
modela al rival con una política concreta (por defecto, la Heurística Básica) y
desciende por la acción que el rival realmente elegiría. Esto:
  - captura mejor la simultaneidad: el modelo decide sobre el estado ANTES de ver
    mi acción (no le damos información que no tiene);
  - evita el pesimismo del minimax paranoid frente a oponentes que no juegan
    para minimizar mi evaluación.

Reutiliza de MinimaxAgent la función de evaluación, la simulación de turno y el
panel "cerebro". Mantiene el MinimaxAgent intacto: es un agente adicional.
"""
import time
from ai.minimax_agent import MinimaxAgent
from ai.heuristic_basic import HeuristicBasicAgent
from engine.state import BattleState


class ExpectimaxAgent(MinimaxAgent):
    def __init__(self, depth: int = 2, weights: list[float] | None = None,
                 model=None, model_name: str = "H.Basica"):
        super().__init__(depth=depth, weights=weights)
        self.model = model if model is not None else HeuristicBasicAgent()
        self._model_name = model_name
        self.name = f"Expectimax d={depth}"

    def get_info_lines(self) -> list[str]:
        return [
            f"Busqueda modelando al rival ({self._model_name}), profundidad {self.depth}.",
            "No asume el peor caso: predice la jugada real del oponente.",
        ]

    # ── Punto de entrada ──────────────────────────────────────────────────────

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        opp_id = 3 - player_id
        self._nodes = 0
        self._prunes = 0
        t0 = time.perf_counter()

        me  = state.get_active(player_id)
        opp = state.get_active(opp_id)

        best_score  = float("-inf")
        best_action = None
        best_idx    = 0
        evaluations = []

        for action in self._possible_actions(state, player_id):
            score = self._search(state, self.depth, player_id, opp_id, action)
            damage = self._action_damage(state, player_id, action)
            evaluations.append({
                "name":         self._action_label(state, player_id, action),
                "damage":       damage,
                "opp_hp_after": max(0, opp.current_hp - damage),
                "opp_max_hp":   opp.max_hp,
                "my_hp_ratio":  me.hp_ratio(),
                "score":        score,
                "chosen":       False,
            })
            if score > best_score:
                best_score  = score
                best_action = action
                best_idx    = len(evaluations) - 1

        if evaluations:
            evaluations[best_idx]["chosen"] = True

        # Réplica predicha del rival según el modelo (para la variante principal).
        opp_pred = self.model.choose_action(state, opp_id)
        pv = (f"yo: {self._action_label(state, player_id, best_action)}  ->  "
              f"rival ({self._model_name}): {self._action_label(state, opp_id, opp_pred)}"
              if best_action is not None else "")

        self.last_brain_data = {
            "formula":     f"expectimax vs modelo {self._model_name} (d={self.depth})",
            "evaluations": evaluations,
            "stats": {"nodos": self._nodes, "podas": 0,
                      "depth": self.depth,
                      "ms": (time.perf_counter() - t0) * 1000.0},
            "pv": pv,
        }
        return best_action

    # ── Búsqueda: yo maximizo; el rival sigue su política (modelo) ─────────────

    def _search(self, state: BattleState, depth: int,
                player_id: int, opp_id: int, my_action: dict) -> float:
        self._nodes += 1
        if state.is_terminal():
            return self._evaluate_terminal(state, player_id)

        # El rival elige sobre el estado actual (no ve mi acción) → simultáneo.
        opp_action = self.model.choose_action(state, opp_id)
        sim = state.copy()
        self._apply_turn(sim, player_id, my_action, opp_action)

        if depth <= 1 or sim.is_terminal():
            return (self._evaluate_terminal(sim, player_id)
                    if sim.is_terminal() else self._evaluate(sim, player_id))

        # Mi mejor respuesta en el siguiente turno (nodo MAX).
        best = float("-inf")
        for action in self._possible_actions(sim, player_id):
            val = self._search(sim, depth - 1, player_id, opp_id, action)
            if val > best:
                best = val
        return best
