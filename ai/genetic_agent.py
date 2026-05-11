"""
Agente cuya función heurística fue optimizada por un Algoritmo Genético.
Es esencialmente HeuristicaAvanzada con pesos evolucionados.
"""
import json
from ai.heuristic_advanced import HeuristicAdvancedAgent


class GeneticAgent(HeuristicAdvancedAgent):
    """
    HeuristicaAvanzada con pesos evolucionados por AG.
    Hereda toda la lógica de evaluación y decisión;
    solo difiere en nombre, pesos y la información que muestra al usuario.
    """

    def __init__(self, weights: list[float], metadata: dict | None = None):
        super().__init__(weights=weights)
        meta = metadata or {}

        self._gens  = meta.get("generations",       "?")
        self._pop   = meta.get("pop_size",           "?")
        self._fit   = meta.get("fitness",            0.0)
        self._bpe   = meta.get("battles_per_eval",   "?")

        self.name              = f"Genetico g={self._gens}"
        self.battles_trained   = self._gens
        self.win_rate_training = self._fit

    # ── Información para consola y selector ───────────────────────────────────

    def get_info_lines(self) -> list[str]:
        labels = ["superv.", "hp_diff", "tipo", "vel."]
        w      = self.weights
        w_str  = "  ".join(f"{l}:{w[i]:.2f}" for i, l in enumerate(labels))
        return [
            "HeuristicaAvanzada optimizada con Algoritmo Genetico.",
            f"Generaciones: {self._gens}  Poblacion: {self._pop}"
            f"  Fitness: {self._fit:.0%}",
            f"Pesos: {w_str}",
        ]

    def get_visual_stats(self) -> list[tuple]:
        """Datos estructurados para la tabla visual del selector GUI."""
        fit_b  = round(self._fit * 4) if isinstance(self._fit, float) else 0
        gen_b  = min(self._gens, 4)   if isinstance(self._gens, int)  else 0
        fit_pct = f"{self._fit:.0%}"  if isinstance(self._fit, float) else "?"
        gen_txt = f"{self._gens} gen" if isinstance(self._gens, int)  else "?"
        return [
            ("Fitness",      fit_b, 4, fit_pct),
            ("Generaciones", gen_b, 4, gen_txt),
            ("Estrategia",   4,     4, "Evolutiva"),
        ]


# ── Carga desde archivo ───────────────────────────────────────────────────────

def load_genetic_agent(path: str) -> GeneticAgent:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return GeneticAgent(weights=data["weights"], metadata=data)
