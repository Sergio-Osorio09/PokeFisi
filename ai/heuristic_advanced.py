from ai.base_agent import Agent
from engine.state import BattleState
from engine.damage import calculate_damage, get_type_multiplier

# Pesos por defecto: [w1, w2, w3, w4, w5, w6]
# Pueden ser reemplazados por los pesos optimizados del algoritmo genético.
DEFAULT_WEIGHTS = [0.30, 0.25, 0.25, 0.10, 0.05, 0.05]

# Velocidad máxima del roster (Mewtwo y Jolteon, SPE=130) para normalizar
MAX_SPEED = 130


class HeuristicAdvancedAgent(Agent):
    """
    Heurística Avanzada — Nivel 3.

    Función de evaluación compuesta (todos los factores normalizados en [0, 1]):

        score = w1 * (vivos_propios / total)
              + w2 * hp_promedio_propio
              - w3 * hp_promedio_oponente
              + w4 * ventaja_de_tipo
              + w5 * diferencia_de_velocidad_normalizada
              - w6 * (vivos_oponente / total)

    A diferencia de la Heurística Básica, esta función considera el equipo
    completo (no solo el Pokémon activo), la ventaja de tipo de los movimientos
    disponibles y la diferencia de velocidades entre los activos.
    """

    def __init__(self, weights: list[float] | None = None):
        super().__init__("Heurística Avanzada")
        self.weights = weights if weights is not None else DEFAULT_WEIGHTS[:]

    # ── Evaluación ────────────────────────────────────────────────────────────

    def _evaluate(self, state: BattleState, player_id: int) -> float:
        opp_id   = 3 - player_id
        my_team  = state.get_team(player_id)
        opp_team = state.get_team(opp_id)
        total    = len(my_team)

        # w1 — Pokémon vivos propios (normalizado sobre el total del equipo)
        alive_mine = sum(1 for p in my_team if p.is_alive()) / total

        # w2 — HP promedio propio normalizado (incluye caídos con hp_ratio=0)
        hp_avg_mine = sum(p.hp_ratio() for p in my_team) / total

        # w3 — HP promedio oponente normalizado
        hp_avg_opp = sum(p.hp_ratio() for p in opp_team) / total

        # w4 — Ventaja de tipo: mejor multiplicador disponible, normalizado a [0, 1]
        #       El máximo posible en nuestro roster es x4 (doble superefectivo)
        me  = state.get_active(player_id)
        opp = state.get_active(opp_id)
        type_adv = self._best_type_advantage(me, opp) / 4.0

        # w5 — Diferencia de velocidades normalizada a [-1, 1], luego a [0, 1]
        speed_diff = (me.speed - opp.speed) / MAX_SPEED          # en [-1, 1]
        speed_norm = (speed_diff + 1) / 2                         # a [0, 1]

        # w6 — Pokémon vivos del oponente (normalizado)
        alive_opp = sum(1 for p in opp_team if p.is_alive()) / total

        w = self.weights
        return (
              w[0] * alive_mine
            + w[1] * hp_avg_mine
            - w[2] * hp_avg_opp
            + w[3] * type_adv
            + w[4] * speed_norm
            - w[5] * alive_opp
        )

    def _best_type_advantage(self, me, opp) -> float:
        """Retorna el mayor multiplicador de tipo entre todos los movimientos disponibles."""
        best = 0.0
        for move in me.get_available_moves():
            mult = get_type_multiplier(move.type, opp.types)
            if mult > best:
                best = mult
        return best

    # ── Decisión ─────────────────────────────────────────────────────────────

    def choose_action(self, state: BattleState, player_id: int) -> dict:
        best_score  = float("-inf")
        best_action = None

        for action in self._possible_actions(state, player_id):
            sim = state.copy()
            self._apply_action(sim, player_id, action)
            score = self._evaluate(sim, player_id)
            if score > best_score:
                best_score  = score
                best_action = action

        return best_action

    def _apply_action(self, state: BattleState, player_id: int, action: dict):
        if action["type"] == "switch":
            state.set_active_index(player_id, action["pokemon_index"])
            return
        move_index = action["move_index"]
        attacker   = state.get_active(player_id)
        defender   = state.get_active(3 - player_id)
        moves      = attacker.get_available_moves()
        if move_index < len(moves):
            dmg, _ = calculate_damage(attacker, moves[move_index], defender)
            defender.take_damage(dmg)
