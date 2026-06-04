import random
import time
from ai.base_agent import Agent
from engine.state import BattleState
from engine.damage import get_type_multiplier

_MAX_SPEED = 130


class MinimaxAgent(Agent):
    """
    Minimax con poda alfa-beta para batallas Pokémon simultáneas.

    Formulación paranoid (árbol alternante):
      - Nodo MAX : yo elijo mi acción para maximizar la evaluación.
      - Nodo MIN : el oponente elige su acción para minimizarla.
      - Cuando ambas acciones están fijadas se simula el turno completo
        (con prioridad por velocidad y auto-reemplazo) y se desciende.

    Cada "profundidad" equivale a un turno de batalla completo.
    La función de evaluación usa los mismos 4 diferenciales de
    HeuristicaAvanzada; los estados terminales valen ±1.
    """

    _WEIGHTS  = [0.40, 0.35, 0.15, 0.10]
    _LABELS   = ["supervivencia", "hp_diff", "tipo", "velocidad"]

    def __init__(self, depth: int = 2, weights: list[float] | None = None):
        super().__init__(f"Minimax d={depth}")
        self.depth = depth
        # Pesos de la función de evaluación. Si no se especifican se usan los
        # ajustados a mano; el Algoritmo Genético los puede sobreescribir.
        self.weights = weights if weights is not None else self._WEIGHTS[:]
        # Datos para el panel "cerebro" de la GUI.
        self.last_brain_data = None
        self._nodes  = 0   # nodos visitados en la búsqueda actual
        self._prunes = 0   # cortes alfa-beta en la búsqueda actual
        # Poda alfa-beta activable; desactivarla permite medir su beneficio.
        self.prune = True

    _MS_PER_DEPTH = {2: 50, 3: 280, 4: 1800}

    def get_info_lines(self) -> list[str]:
        d   = self.depth
        ms  = self._MS_PER_DEPTH.get(d, d * 200)
        return [
            f"Minimax + poda alfa-beta, profundidad {d} turno(s).",
            f"Profundidad: {d}/4   Velocidad: ~{ms}ms/turno",
        ]

    def get_visual_stats(self) -> list[tuple]:
        """Datos estructurados para la GUI: [(label, filled, total, texto_extra)]."""
        d  = self.depth
        ms = self._MS_PER_DEPTH.get(d, d * 200)
        return [
            ("Profundidad", min(d, 4),     4, f"{d} turno(s)"),
            ("Velocidad",   max(1, 5 - d), 4, f"~{ms}ms/turno"),
            ("Precision",   min(d + 1, 4), 4, ""),
        ]

    # ── Punto de entrada ──────────────────────────────────────────────────────

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        opp_id = 3 - player_id
        self._nodes  = 0
        self._prunes = 0
        t0 = time.perf_counter()

        me  = state.get_active(player_id)
        opp = state.get_active(opp_id)

        best_score  = float("-inf")
        best_action = None
        best_idx    = 0
        evaluations = []

        for action in self._possible_actions(state, player_id):
            score = self._minimax(
                state, self.depth,
                float("-inf"), float("inf"),
                player_id, opp_id,
                my_action=action,
            )

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

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        self.last_brain_data = {
            "formula":     f"minimax + poda alfa-beta (d={self.depth}): valor anticipando al rival",
            "evaluations": evaluations,
            "stats": {
                "nodos":  self._nodes,
                "podas":  self._prunes,
                "depth":  self.depth,
                "ms":     elapsed_ms,
            },
            "pv": self._principal_variation(state, player_id, opp_id, best_action),
        }
        return best_action

    # ── Datos para el panel "cerebro" ─────────────────────────────────────────

    def _action_label(self, state, player_id, action) -> str:
        if action["type"] == "move":
            moves = state.get_active(player_id).get_available_moves()
            i = action["move_index"]
            return moves[i].name if i < len(moves) else "?"
        team = state.get_team(player_id)
        return f"-> {team[action['pokemon_index']].name}"

    def _action_damage(self, state, player_id, action) -> int:
        """Daño inmediato del movimiento (solo para la barra; el score es el valor minimax)."""
        if action["type"] != "move":
            return 0
        me    = state.get_active(player_id)
        opp   = state.get_active(3 - player_id)
        moves = me.get_available_moves()
        i     = action["move_index"]
        return self._sim_damage(me, moves[i], opp) if i < len(moves) else 0

    def _principal_variation(self, state, player_id, opp_id, my_action) -> str:
        """Línea predicha: mi mejor acción y la mejor réplica del rival (1 ply)."""
        if my_action is None:
            return ""
        mine = self._action_label(state, player_id, my_action)

        worst = float("inf")
        best_opp = None
        for opp_action in self._possible_actions(state, opp_id):
            sim = state.copy()
            self._apply_turn(sim, player_id, my_action, opp_action)
            val = (self._evaluate_terminal(sim, player_id)
                   if sim.is_terminal() else self._evaluate(sim, player_id))
            if val < worst:
                worst = val
                best_opp = opp_action
        if best_opp is None:
            return f"yo: {mine}"
        rival = self._action_label(state, opp_id, best_opp)
        return f"yo: {mine}  ->  rival: {rival}"

    # ── Minimax recursivo ─────────────────────────────────────────────────────

    def _minimax(self, state: BattleState, depth: int,
                 alpha: float, beta: float,
                 player_id: int, opp_id: int,
                 my_action: dict | None) -> float:
        """
        my_action=None  → nodo MAX: elige mi acción.
        my_action=dict  → nodo MIN: elige acción del oponente, simula turno.
        """
        self._nodes += 1

        if state.is_terminal():
            return self._evaluate_terminal(state, player_id)

        if depth == 0:
            return self._evaluate(state, player_id)

        if my_action is None:
            # ── Nodo MAX ──────────────────────────────────────────────────────
            best = float("-inf")
            for action in self._possible_actions(state, player_id):
                val = self._minimax(state, depth, alpha, beta,
                                    player_id, opp_id, action)
                if val > best:
                    best = val
                if best > alpha:
                    alpha = best
                if beta <= alpha and self.prune:
                    self._prunes += 1
                    break   # poda β
            return best

        else:
            # ── Nodo MIN ──────────────────────────────────────────────────────
            best = float("inf")
            for opp_action in self._possible_actions(state, opp_id):
                sim = state.copy()
                self._apply_turn(sim, player_id, my_action, opp_action)
                val = self._minimax(sim, depth - 1, alpha, beta,
                                    player_id, opp_id, None)
                if val < best:
                    best = val
                if best < beta:
                    beta = best
                if beta <= alpha and self.prune:
                    self._prunes += 1
                    break   # poda α
            return best

    # ── Simulación de turno (sin logging) ────────────────────────────────────

    def _apply_turn(self, state: BattleState, player_id: int,
                    my_action: dict, opp_action: dict):
        opp_id = 3 - player_id
        me  = state.get_active(player_id)
        opp = state.get_active(opp_id)

        me_first = me.speed > opp.speed or (me.speed == opp.speed and random.random() < 0.5)
        if me_first:
            self._apply_action(state, player_id, my_action)
            if not state.is_terminal():
                self._apply_action(state, opp_id, opp_action)
        else:
            self._apply_action(state, opp_id, opp_action)
            if not state.is_terminal():
                self._apply_action(state, player_id, my_action)

        self._auto_replace(state, player_id)
        self._auto_replace(state, opp_id)

    def _apply_action(self, state: BattleState, player_id: int, action: dict):
        if action["type"] == "switch":
            state.set_active_index(player_id, action["pokemon_index"])
            return
        attacker = state.get_active(player_id)
        defender = state.get_active(3 - player_id)
        moves    = attacker.get_available_moves()
        idx      = action["move_index"]
        if attacker.is_alive() and idx < len(moves):
            defender.take_damage(self._sim_damage(attacker, moves[idx], defender))

    def _auto_replace(self, state: BattleState, player_id: int):
        if not state.get_active(player_id).is_alive():
            idx = state.next_alive_index(player_id)
            if idx >= 0:
                state.set_active_index(player_id, idx)

    # ── Evaluación heurística ─────────────────────────────────────────────────

    def _evaluate_terminal(self, state: BattleState, player_id: int) -> float:
        winner = state.get_winner()
        if winner == player_id:
            return 1.0
        if winner is not None:
            return -1.0
        return 0.0

    def _evaluate(self, state: BattleState, player_id: int) -> float:
        opp_id   = 3 - player_id
        my_team  = state.get_team(player_id)
        opp_team = state.get_team(opp_id)
        total    = len(my_team)

        alive_diff = (
            sum(1 for p in my_team  if p.is_alive()) -
            sum(1 for p in opp_team if p.is_alive())
        ) / total

        hp_diff = (
            sum(p.hp_ratio() for p in my_team)  / total -
            sum(p.hp_ratio() for p in opp_team) / total
        )

        me  = state.get_active(player_id)
        opp = state.get_active(opp_id)
        type_adv = (
            self._best_type_mult(me, opp) -
            self._best_type_mult(opp, me)
        ) / 4.0

        speed_adv = (me.speed - opp.speed) / _MAX_SPEED

        w = self.weights
        return (
              w[0] * alive_diff
            + w[1] * hp_diff
            + w[2] * type_adv
            + w[3] * speed_adv
        )

    def _best_type_mult(self, attacker, defender) -> float:
        best = 0.0
        for move in attacker.get_available_moves():
            m = get_type_multiplier(move.type, defender.types)
            if m > best:
                best = m
        return best
