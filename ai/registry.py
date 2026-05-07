"""
Registro central de agentes disponibles.
Cargado una vez al inicio; incluye automáticamente los agentes entrenados
que existan en data/weights_*.json.
"""
import json
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent
from ai.heuristic_trained import HeuristicTrainedAgent, find_trained_weights

_BASE: list[tuple[str, object]] = [
    ("Agente Aleatorio",    lambda: RandomAgent()),
    ("Heuristica Basica",   lambda: HeuristicBasicAgent()),
    ("Heuristica Avanzada", lambda: HeuristicAdvancedAgent()),
]


def _trained_entries() -> list[tuple[str, object]]:
    entries = []
    for path in find_trained_weights():
        p = path
        with open(p) as f:
            n = json.load(f)["battles"]
        entries.append((f"HeuristicaAvanzada-{n}", lambda p=p: HeuristicTrainedAgent(p)))
    return entries


def build_registry() -> list[tuple[str, object]]:
    """Construye la lista de (nombre, factory) escaneando data/ en cada llamada."""
    return _BASE + _trained_entries()


# Instancia estática para uso en GUI (snapshot al inicio del proceso)
AI_REGISTRY: list[tuple[str, object]] = build_registry()

# Info lines pre-computadas por índice (mismo orden que AI_REGISTRY)
AI_INFO: list[list[str]] = [factory().get_info_lines() for _, factory in AI_REGISTRY]
