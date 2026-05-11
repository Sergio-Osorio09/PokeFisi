from ai.base_agent import Agent
from engine.state import BattleState
from engine.damage import calculate_damage, get_type_multiplier

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

    def __init__(self, depth: int = 2):
        super().__init__(f"Minimax d={depth}")
        self.depth = depth

    def get_info_lines(self) -> list[str]:
        w = self._WEIGHTS
        w_str = "  ".join(f"{l}:{w[i]:.2f}" for i, l in enumerate(self._LABELS))
        return [
            f"Minimax + poda alfa-beta, profundidad {self.depth} turno(s).",
            f"Pesos heurísticos: {w_str}",
        ]

    # ── Punto de entrada ──────────────────────────────────────────────────────

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        opp_id = 3 - player_id
        best_score  = float("-inf")
        best_action = None

        for action in self._possible_actions(state, player_id):
            score = self._minimax(
                state, self.depth,
                float("-inf"), float("inf"),
                player_id, opp_id,
                my_action=action,
            )
            if score > best_score:
                best_score  = score
                best_action = action

        return best_action

    # ── Minimax recursivo ─────────────────────────────────────────────────────

    def _minimax(self, state: BattleState, depth: int,
                 alpha: float, beta: float,
                 player_id: int, opp_id: int,
                 my_action: dict | None) -> float:
        """
        my_action=None  → nodo MAX: elige mi acción.
        my_action=dict  → nodo MIN: elige acción del oponente, simula turno.
        """
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
                if beta <= alpha:
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
                if beta <= alpha:
                    break   # poda α
            return best

    # ── Simulación de turno (sin logging) ────────────────────────────────────

    def _apply_turn(self, state: BattleState, player_id: int,
                    my_action: dict, opp_action: dict):
        opp_id = 3 - player_id
        me  = state.get_active(player_id)
        opp = state.get_active(opp_id)

        if me.speed >= opp.speed:
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
            dmg, _ = calculate_damage(attacker, moves[idx], defender)
            defender.take_damage(dmg)

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

        w = self._WEIGHTS
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
