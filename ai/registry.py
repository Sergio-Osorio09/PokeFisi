"""
Registro central de agentes disponibles.
Cargado una vez al inicio; incluye automáticamente los agentes entrenados
que existan en data/weights_*.json y data/genetic_*.json.
"""
import json
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent
from ai.heuristic_trained import HeuristicTrainedAgent, find_trained_weights
from ai.minimax_agent import MinimaxAgent
from ai.genetic_agent import GeneticAgent, load_genetic_agent
from ai.genetic_trainer import find_genetic_weights
from ai.heuristic_improved import HeuristicImprovedAgent, HeuristicImprovedTrainedAgent, find_improved_weights

_BASE: list[tuple[str, object]] = [
    ("Agente Aleatorio",    lambda: RandomAgent()),
    ("Heuristica Basica",   lambda: HeuristicBasicAgent()),
    ("Heuristica Avanzada", lambda: HeuristicAdvancedAgent()),
    ("Heuristica Mejorada", lambda: HeuristicImprovedAgent()),
    ("Minimax d=2",         lambda: MinimaxAgent(depth=2)),
    ("Minimax d=3",         lambda: MinimaxAgent(depth=3)),
]


def _trained_entries() -> list[tuple[str, object]]:
    entries = []
    for path in find_trained_weights():
        p = path
        with open(p) as f:
            n = json.load(f)["battles"]
        entries.append((f"HeuristicaAvanzada-{n}", lambda p=p: HeuristicTrainedAgent(p)))
    return entries


def _genetic_entries() -> list[tuple[str, object]]:
    entries = []
    for path in find_genetic_weights():
        p = path
        with open(p) as f:
            data = json.load(f)
        gens = data.get("generations", "?")
        pop  = data.get("pop_size",    "?")
        entries.append((f"Genetico g={gens} p={pop}",
                        lambda p=p: load_genetic_agent(p)))
    return entries


def _improved_trained_entries() -> list[tuple[str, object]]:
    entries = []
    for path in find_improved_weights():
        p = path
        with open(p) as f:
            n = json.load(f)["battles"]
        entries.append((f"H.Mejorada-{n}", lambda p=p: HeuristicImprovedTrainedAgent(p)))
    return entries


def build_registry() -> list[tuple[str, object]]:
    """Construye la lista de (nombre, factory) escaneando data/ en cada llamada."""
    return _BASE + _trained_entries() + _improved_trained_entries() + _genetic_entries()


# Instancia estática para uso en GUI (snapshot al inicio del proceso)
AI_REGISTRY: list[tuple[str, object]] = build_registry()

# Info lines pre-computadas por índice (mismo orden que AI_REGISTRY)
AI_INFO: list[list[str]] = [factory().get_info_lines() for _, factory in AI_REGISTRY]
