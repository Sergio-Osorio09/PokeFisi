"""
Agente Minimax cuya función de evaluación fue optimizada por un Algoritmo Genético.
Es esencialmente MinimaxAgent (poda alfa-beta) con los 4 pesos evolucionados.
"""
import json
from ai.minimax_agent import MinimaxAgent


class GeneticAgent(MinimaxAgent):
    """
    MinimaxAgent con los pesos de su función de evaluación evolucionados por AG.
    Hereda toda la lógica de búsqueda (minimax + poda alfa-beta) y evaluación;
    solo difiere en nombre, pesos y la información que muestra al usuario.
    """

    def __init__(self, weights: list[float], metadata: dict | None = None):
        meta = metadata or {}
        self._depth = meta.get("minimax_depth", 2)
        super().__init__(depth=self._depth, weights=weights)

        self._gens  = meta.get("generations",       "?")
        self._pop   = meta.get("pop_size",           "?")
        self._fit   = meta.get("fitness",            0.0)
        self._bpe   = meta.get("battles_per_eval",   "?")

        self.name              = f"Genetico g={self._gens} d={self._depth}"
        self.battles_trained   = self._gens
        self.win_rate_training = self._fit

    # ── Información para consola y selector ───────────────────────────────────

    def get_info_lines(self) -> list[str]:
        labels = ["superv.", "hp_diff", "tipo", "vel."]
        w      = self.weights
        w_str  = "  ".join(f"{l}:{w[i]:.2f}" for i, l in enumerate(labels))
        return [
            f"Minimax (poda alfa-beta, d={self._depth}) optimizado con Algoritmo Genetico.",
            f"Generaciones: {self._gens}  Poblacion: {self._pop}"
            f"  Fitness: {self._fit:.0%}",
            f"Pesos: {w_str}",
        ]

    def choose_action(self, state, player_id):
        # Reusa toda la búsqueda minimax + panel cerebro del padre, y añade
        # los pesos aprendidos (vs base) para mostrar su "personalidad".
        action = super().choose_action(state, player_id)
        if self.last_brain_data is not None:
            labels = ["superv", "hp", "tipo", "vel"]
            base   = self._WEIGHTS
            self.last_brain_data["formula"] = (
                f"minimax evolucionado (g={self._gens}, fitness {self._fit:.0%})")
            self.last_brain_data["weights"] = [
                (labels[i], self.weights[i], base[i]) for i in range(len(labels))
            ]
        return action

    def get_visual_stats(self) -> list[tuple]:
        """Datos estructurados para la tabla visual del selector GUI."""
        fit_b  = round(self._fit * 4) if isinstance(self._fit, float) else 0
        gen_b  = min(self._gens, 4)   if isinstance(self._gens, int)  else 0
        fit_pct = f"{self._fit:.0%}"  if isinstance(self._fit, float) else "?"
        gen_txt = f"{self._gens} gen" if isinstance(self._gens, int)  else "?"
        return [
            ("Fitness",      fit_b,                4, fit_pct),
            ("Generaciones", gen_b,                4, gen_txt),
            ("Profundidad",  min(self._depth, 4),  4, f"{self._depth} turno(s)"),
        ]


# ── Carga desde archivo ───────────────────────────────────────────────────────

def load_genetic_agent(path: str) -> GeneticAgent:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return GeneticAgent(weights=data["weights"], metadata=data)
