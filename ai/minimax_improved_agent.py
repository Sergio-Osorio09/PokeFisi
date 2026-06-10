"""
Minimax con poda alfa-beta cuya función de evaluación es la de la
Heurística MEJORADA (6 componentes) en lugar de la Avanzada (4).

    score = w0*superv + w1*hp_pond + w2*ko_threat
          + w3*ko_danger + w4*cobertura + w5*vel

Hereda toda la búsqueda (paranoid + poda alfa-beta) de MinimaxAgent y solo
sustituye la evaluación de las hojas. Es la base del Genético Mejorado: el
AG evoluciona estos 6 pesos.
"""
from ai.minimax_agent import MinimaxAgent
from engine.state import BattleState
from engine.damage import get_type_multiplier

# Mismos valores por defecto que HeuristicImprovedAgent.
DEFAULT_WEIGHTS_6 = [0.25, 0.20, 0.20, 0.15, 0.10, 0.10]
_LABELS_6         = ["superv", "hp_pond", "ko+", "ko-", "cob", "vel"]
_MAX_SPEED        = 130


class MinimaxImprovedAgent(MinimaxAgent):
    """MinimaxAgent con evaluación de hojas de 6 componentes (H. Mejorada)."""

    _LABELS = _LABELS_6

    def __init__(self, depth: int = 2, weights: list[float] | None = None):
        super().__init__(depth=depth,
                         weights=weights if weights is not None else DEFAULT_WEIGHTS_6[:])
        self.name = f"Minimax-Mej d={depth}"

    def get_info_lines(self) -> list[str]:
        w     = self.weights
        w_str = "  ".join(f"{l}:{w[i]:.2f}" for i, l in enumerate(_LABELS_6))
        return [
            f"Minimax + poda alfa-beta (d={self.depth}) con evaluación de 6 componentes.",
            f"Pesos: {w_str}",
        ]

    # ── Evaluación de 6 componentes (idéntica a HeuristicImprovedAgent) ──────

    def _evaluate(self, state: BattleState, player_id: int) -> float:
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

        # w3 — ko_danger: negativo según el daño que puede hacerme el rival [-1, 0]
        max_opp_dmg = max(
            (self._sim_damage(opp, mv, me) for mv in opp.get_available_moves()),
            default=0,
        )
        raw_danger   = min(1.0, max_opp_dmg / max(1, me.current_hp))
        speed_factor = 0.5 if me.speed > opp.speed else 1.0
        ko_danger    = -raw_danger * speed_factor

        # w4 — cobertura del equipo completo [-1, 1]
        my_alive  = [p for p in my_team  if p.is_alive()]
        opp_alive = [p for p in opp_team if p.is_alive()]
        cobertura = self._coverage(my_alive, opp_alive) - self._coverage(opp_alive, my_alive)

        # w5 — velocidad del activo [-1, 1]
        vel = (me.speed - opp.speed) / _MAX_SPEED

        w = self.weights
        return (w[0] * superv + w[1] * hp_pond + w[2] * ko_threat
                + w[3] * ko_danger + w[4] * cobertura + w[5] * vel)

    @staticmethod
    def _coverage(attackers, defenders) -> float:
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
