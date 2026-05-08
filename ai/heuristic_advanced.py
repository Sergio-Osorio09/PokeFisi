from ai.base_agent import Agent
from engine.state import BattleState
from engine.damage import calculate_damage, get_type_multiplier

# Pesos por defecto: [w0, w1, w2, w3]
# Cada peso pondera un diferencial (mi_valor - valor_oponente),
# por lo que el score es 0 en un estado perfectamente simétrico.
DEFAULT_WEIGHTS = [0.40, 0.35, 0.15, 0.10]

# Velocidad máxima del roster (Mewtwo y Jolteon, SPE=130) para normalizar
MAX_SPEED = 130


class HeuristicAdvancedAgent(Agent):
    """
    Heurística Avanzada — Nivel 3.

    Función de evaluación basada en diferenciales (todos en [-1, 1]):

        score = w0 * (vivos_propios - vivos_oponente) / total
              + w1 * (hp_promedio_propio - hp_promedio_oponente)
              + w2 * ventaja_de_tipo            ∈ [0, 1]
              + w3 * ventaja_de_velocidad        ∈ [-1, 1]

    El estado simétrico produce score = 0.
    Cada peso expresa la importancia relativa de ese diferencial.
    """

    _LABELS = ["supervivencia", "hp_diff", "tipo", "velocidad"]

    def __init__(self, weights: list[float] | None = None):
        super().__init__("Heurística Avanzada")
        self.weights = weights if weights is not None else DEFAULT_WEIGHTS[:]

    def get_info_lines(self) -> list[str]:
        w = self.weights
        w_str = "  ".join(f"{l}:{w[i]:.2f}" for i, l in enumerate(self._LABELS))
        return [
            "Evalua 4 diferenciales: supervivencia, HP, tipo, velocidad.",
            f"Pesos: {w_str}",
        ]

    # ── Evaluación ────────────────────────────────────────────────────────────

    def _evaluate(self, state: BattleState, player_id: int) -> float:
        opp_id   = 3 - player_id
        my_team  = state.get_team(player_id)
        opp_team = state.get_team(opp_id)
        total    = len(my_team)

        # w0 — Diferencial de supervivencia: (vivos_propios - vivos_oponente) / total
        #       Rango [-1, 1]. Positivo = tengo más Pokémon vivos.
        alive_diff = (
            sum(1 for p in my_team  if p.is_alive()) -
            sum(1 for p in opp_team if p.is_alive())
        ) / total

        # w1 — Diferencial de HP promedio: hp_propio - hp_oponente
        #       Rango [-1, 1]. Positivo = mi equipo tiene más vida en promedio.
        hp_diff = (
            sum(p.hp_ratio() for p in my_team)  / total -
            sum(p.hp_ratio() for p in opp_team) / total
        )

        # w2 — Diferencial de tipo: (mi_mejor_mult - mejor_mult_oponente) / 4.0
        #       Rango [-1, 1]. Positivo = tengo mejor ventaja de tipo que el oponente.
        me  = state.get_active(player_id)
        opp = state.get_active(opp_id)
        type_adv = (
            self._best_type_advantage(me, opp) -
            self._best_type_advantage(opp, me)
        ) / 4.0

        # w3 — Ventaja de velocidad: (vel_propia - vel_oponente) / MAX_SPEED
        #       Rango [-1, 1]. Positivo = soy más rápido (actúo primero).
        speed_adv = (me.speed - opp.speed) / MAX_SPEED

        w = self.weights
        return (
              w[0] * alive_diff
            + w[1] * hp_diff
            + w[2] * type_adv
            + w[3] * speed_adv
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
