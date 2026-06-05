"""
Entrenador basado en Algoritmos Genéticos sobre Minimax.

Optimiza los 4 pesos de la función de evaluación de MinimaxAgent (poda
alfa-beta) buscando la combinación que maximiza el win-rate en batallas
contra HeuristicaBasica. El AG evoluciona los pesos; cada individuo se mide
jugando con un MinimaxAgent que usa esos pesos.
"""
import random
import json
import os

from engine.loader import load_moves, build_team, load_all_pokemon
from engine.state import BattleState
from engine.battle import Battle
from ai.minimax_agent import MinimaxAgent
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent


def default_opponent_panel() -> list:
    """Panel de rivales recomendado para el fitness: cubre un rango de
    dificultad (azar, heurística simple y heurística avanzada). Entrenar contra
    el panel produce pesos más robustos y que generalizan mejor que entrenar
    contra un único rival (ver Experimento D del informe)."""
    return [RandomAgent, HeuristicBasicAgent, HeuristicAdvancedAgent]

_DATA_DIR = "data"
_N_WEIGHTS = 4


# ── Operadores genéticos ──────────────────────────────────────────────────────

def _normalize(weights: list[float]) -> list[float]:
    total = sum(weights)
    if total <= 0:
        return [1 / _N_WEIGHTS] * _N_WEIGHTS
    return [max(0.0, w / total) for w in weights]


def _random_individual() -> list[float]:
    return _normalize([random.random() for _ in range(_N_WEIGHTS)])


def _make_scenarios(all_ids: list[int], n: int, n_opp: int = 1) -> list[tuple]:
    """Genera n escenarios (equipo1, equipo2, semilla, idx_rival). Se comparten
    entre todos los individuos de una generación (Common Random Numbers): así las
    diferencias de fitness reflejan los pesos y no la suerte. Cuando hay varios
    rivales, se reparten de forma cíclica entre los escenarios."""
    return [(random.sample(all_ids, 3),
             random.sample(all_ids, 3),
             random.randrange(2 ** 31),
             i % n_opp) for i in range(n)]


def _evaluate(weights: list[float], all_moves: dict, depth: int,
              scenarios: list[tuple], opponents: list,
              should_stop=None, battle_cb=None) -> float:
    """Fitness = win-rate de un MinimaxAgent (poda alfa-beta) con estos pesos,
    jugando exactamente los 'scenarios' dados (equipos y semilla fijos) contra
    el panel de 'opponents' (factories). Reusar los mismos escenarios reduce la
    varianza; usar varios rivales reduce el sobreajuste a uno solo.

    should_stop : si devuelve True, corta entre batallas (cancelación granular).
    battle_cb   : se llama tras cada batalla jugada (para reportar progreso fino)."""
    agent  = MinimaxAgent(depth=depth, weights=weights)
    wins   = 0
    played = 0
    for ids1, ids2, seed, opp_idx in scenarios:
        if should_stop is not None and should_stop():
            break
        random.seed(seed)   # mismo emparejamiento y azar para todos los individuos
        opponent = opponents[opp_idx]()
        state = BattleState(build_team(ids1, all_moves), build_team(ids2, all_moves))
        if Battle(state, agent, opponent).run() == 1:
            wins += 1
        played += 1
        if battle_cb is not None:
            battle_cb()
    return wins / played if played else 0.0


def _tournament(population: list, fitnesses: list[float], k: int = 3) -> list[float]:
    """Selección por torneo: k candidatos aleatorios, gana el de mayor fitness."""
    candidates = random.sample(range(len(population)), k)
    best       = max(candidates, key=lambda i: fitnesses[i])
    return population[best][:]


def _crossover(p1: list[float], p2: list[float]) -> list[float]:
    """Crossover uniforme: cada gen se hereda aleatoriamente de uno de los padres."""
    child = [p1[i] if random.random() < 0.5 else p2[i] for i in range(_N_WEIGHTS)]
    return _normalize(child)


def _mutate(individual: list[float], rate: float, strength: float) -> list[float]:
    """Mutación gaussiana: cada gen se perturba con probabilidad 'rate'."""
    result = individual[:]
    for i in range(_N_WEIGHTS):
        if random.random() < rate:
            result[i] += random.gauss(0, strength)
            result[i]  = max(0.0, result[i])
    return _normalize(result)


# ── Ciclo principal ───────────────────────────────────────────────────────────

def run_genetic(pop_size: int = 12,
                generations: int = 15,
                battles_per_eval: int = 20,
                minimax_depth: int = 2,
                mutation_rate: float = 0.15,
                mutation_strength: float = 0.10,
                elite_k: int = 2,
                opponent_factories=None,
                callback=None,
                should_stop=None,
                progress_cb=None) -> dict:
    """
    Ejecuta el algoritmo genético completo sobre Minimax.

    Cada individuo es un vector de 4 pesos que se inyecta en la función de
    evaluación de un MinimaxAgent (poda alfa-beta). Como el minimax es mucho
    más costoso que la heurística directa, los valores por defecto de
    población/generaciones/batallas son más conservadores.

    Parameters
    ----------
    pop_size          : número de individuos por generación
    generations       : número de generaciones a evolucionar
    battles_per_eval  : batallas que juega cada individuo para medir su fitness.
                        Más batallas = fitness menos ruidoso; se usan los mismos
                        escenarios para todos los individuos de la generación (CRN)
    minimax_depth     : profundidad del MinimaxAgent usado para evaluar cada individuo
    mutation_rate     : probabilidad de mutar cada gen  [0, 1]
    mutation_strength : desviación estándar de la mutación gaussiana
    elite_k           : cuántos mejores individuos pasan sin cambios a la siguiente gen
    callback          : función opcional llamada al final de cada generación con
                        (gen, total, best_gen_fit, best_global_fit, avg_fit, population)
    should_stop       : callable opcional sin args; si devuelve True se detiene la
                        evolución (se comprueba entre batallas → cancelación rápida)
                        y se retorna el mejor resultado obtenido hasta ese momento
    progress_cb       : callable opcional para progreso fino, llamado tras cada
                        batalla con (battles_done, total_battles, gen, generations,
                        best_global_fit)

    Returns
    -------
    dict con weights, fitness, historial y parámetros usados.
    """
    all_moves = load_moves()
    all_ids   = [p["id"] for p in load_all_pokemon()]

    # Panel de rivales para el fitness. Por defecto solo HeuristicaBasica; pasar
    # varias factories entrena contra un panel (reduce el sobreajuste a un rival).
    if opponent_factories is None:
        opponent_factories = [HeuristicBasicAgent]
    n_opp = len(opponent_factories)

    # Inicialización: población aleatoria
    population = [_random_individual() for _ in range(pop_size)]

    best_weights  = None
    best_fitness  = -1.0
    history: list[dict] = []

    total_battles = pop_size * generations * battles_per_eval
    battles_done  = 0
    actual_gens   = 0

    for gen in range(1, generations + 1):

        # Escenarios compartidos por toda la generación (Common Random Numbers):
        # todos los individuos se miden con los mismos emparejamientos y azar.
        scenarios = _make_scenarios(all_ids, battles_per_eval, n_opp)

        # ── 1. Evaluación (con progreso y cancelación por batalla) ────────────
        fitnesses: list[float] = []
        for w in population:
            if should_stop is not None and should_stop():
                break

            def _battle_cb():
                nonlocal battles_done
                battles_done += 1
                if progress_cb is not None:
                    progress_cb(battles_done, total_battles, gen,
                                generations, max(best_fitness, 0.0))

            f = _evaluate(w, all_moves, minimax_depth, scenarios, opponent_factories,
                          should_stop=should_stop, battle_cb=_battle_cb)
            fitnesses.append(f)

            # Mejor global incremental (no se pierde aunque se cancele a media gen)
            if f > best_fitness:
                best_fitness = f
                best_weights = w[:]

        if not fitnesses:
            break   # cancelado antes de evaluar nada en esta generación

        actual_gens  = gen
        gen_best_fit = max(fitnesses)
        avg_fit      = sum(fitnesses) / len(fitnesses)

        history.append({
            "gen":          gen,
            "best_gen":     round(gen_best_fit, 4),
            "best_global":  round(best_fitness, 4),
            "avg":          round(avg_fit, 4),
            "best_weights": best_weights[:],
        })

        if callback:
            callback(gen, generations, gen_best_fit, best_fitness,
                     avg_fit, population[:])

        # Cancelado a media generación o señal de parada: terminar aquí.
        if len(fitnesses) < pop_size or (should_stop is not None and should_stop()):
            break

        # ── 2. Elitismo ───────────────────────────────────────────────────────
        sorted_pairs = sorted(zip(fitnesses, population), reverse=True)
        new_pop      = [ind for _, ind in sorted_pairs[:elite_k]]

        # ── 3. Reproducción ───────────────────────────────────────────────────
        while len(new_pop) < pop_size:
            p1    = _tournament(population, fitnesses)
            p2    = _tournament(population, fitnesses)
            child = _crossover(p1, p2)
            child = _mutate(child, mutation_rate, mutation_strength)
            new_pop.append(child)

        population = new_pop

    if best_weights is None:          # salvaguarda: nunca se evaluó nada
        best_weights = population[0][:]
        best_fitness = max(best_fitness, 0.0)

    return {
        "weights":           best_weights,
        "fitness":           best_fitness,
        "generations":       actual_gens or generations,
        "pop_size":          pop_size,
        "battles_per_eval":  battles_per_eval,
        "minimax_depth":     minimax_depth,
        "mutation_rate":     mutation_rate,
        "mutation_strength": mutation_strength,
        "elite_k":           elite_k,
        "opponents":         [c().name for c in opponent_factories],
        "history":           history,
    }


# ── I/O ───────────────────────────────────────────────────────────────────────

def save_genetic_weights(data: dict) -> str:
    os.makedirs(_DATA_DIR, exist_ok=True)
    depth = data.get("minimax_depth", 2)
    tag   = f"g{data['generations']}_p{data['pop_size']}_d{depth}"
    path  = os.path.join(_DATA_DIR, f"genetic_{tag}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def find_genetic_weights():
    """Genera las rutas de archivos genetic_*.json en data/."""
    if not os.path.isdir(_DATA_DIR):
        return
    for fname in sorted(os.listdir(_DATA_DIR)):
        if fname.startswith("genetic_") and fname.endswith(".json"):
            yield os.path.join(_DATA_DIR, fname)
