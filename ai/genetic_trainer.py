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


def _team_strength(team: list) -> float:
    """Fuerza restante de un equipo en [0, 1]: combina Pokémon vivos y HP.
    1.0 = equipo completo a tope; 0.0 = todos derrotados."""
    total = len(team)
    if total == 0:
        return 0.0
    alive = sum(1 for p in team if p.is_alive())
    hp    = sum(p.hp_ratio() for p in team)
    return (alive + hp) / (2 * total)


def _evaluate(weights: list[float], all_moves: dict, depth: int,
              scenarios: list[tuple], opponents: list,
              should_stop=None, battle_cb=None) -> tuple[float, float]:
    """Mide unos pesos jugando exactamente los 'scenarios' dados (equipos y
    semilla fijos) contra el panel de 'opponents' (factories). Devuelve:

        (win_rate, fitness_continuo)

    - win_rate         : fracción de batallas ganadas (métrica intuitiva; se muestra).
    - fitness_continuo : promedio de una recompensa suave por batalla
          recompensa = 0.5 + 0.5·(fuerza_mía − fuerza_rival)   ∈ [0, 1]
      que da gradiente aunque el win/loss no cambie (ganar 3-0 ≠ ganar 1-0).
      Es la señal que usa la SELECCIÓN del AG.

    should_stop : si devuelve True, corta entre batallas (cancelación granular).
    battle_cb   : se llama tras cada batalla jugada (para reportar progreso fino)."""
    agent      = MinimaxAgent(depth=depth, weights=weights)
    wins       = 0
    played     = 0
    reward_sum = 0.0
    for ids1, ids2, seed, opp_idx in scenarios:
        if should_stop is not None and should_stop():
            break
        random.seed(seed)   # mismo emparejamiento y azar para todos los individuos
        opponent = opponents[opp_idx]()
        # El agente entrenado es el jugador 1 → su equipo es player1_team.
        state  = BattleState(build_team(ids1, all_moves), build_team(ids2, all_moves))
        winner = Battle(state, agent, opponent).run()
        if winner == 1:
            wins += 1
        # Recompensa continua según la fuerza restante de cada lado al terminar.
        reward_sum += 0.5 + 0.5 * (_team_strength(state.player1_team) -
                                   _team_strength(state.player2_team))
        played += 1
        if battle_cb is not None:
            battle_cb()
    if not played:
        return 0.0, 0.0
    return wins / played, reward_sum / played


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
                train_depth: int | None = None,
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
    minimax_depth     : profundidad de JUEGO del agente resultante (se guarda en el
                        JSON y la usa GeneticAgent al jugar)
    train_depth       : profundidad usada SOLO para medir el fitness durante el
                        entrenamiento. Por defecto = minimax_depth. En 1 entrena
                        mucho más rápido y con más señal; luego se juega a minimax_depth
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

    # Profundidad para medir el fitness durante el entrenamiento. Por defecto la
    # de juego; ponerla en 1 (desde la GUI) entrena ~13x más rápido y con más
    # señal, mientras el agente resultante sigue jugando a 'minimax_depth'.
    eval_depth = train_depth if train_depth is not None else minimax_depth

    # Escenarios FIJOS para TODA la corrida (no solo por generación): así el
    # fitness es comparable entre generaciones y la curva "mejor global" sube de
    # verdad, en vez de quedarse clavada en un máximo afortunado temprano.
    scenarios = _make_scenarios(all_ids, battles_per_eval, n_opp)

    # Inicialización: población aleatoria
    population = [_random_individual() for _ in range(pop_size)]

    best_weights = None
    best_score   = -1.0     # fitness continuo del mejor (señal de SELECCIÓN)
    best_winrate = 0.0      # win-rate del mejor (métrica que se muestra/guarda)
    history: list[dict] = []

    total_battles = pop_size * generations * battles_per_eval
    battles_done  = 0
    actual_gens   = 0

    for gen in range(1, generations + 1):

        # ── 1. Evaluación (con progreso y cancelación por batalla) ────────────
        scores:   list[float] = []   # fitness continuo (selección)
        winrates: list[float] = []   # win-rate (visualización)
        for w in population:
            if should_stop is not None and should_stop():
                break

            def _battle_cb():
                nonlocal battles_done
                battles_done += 1
                if progress_cb is not None:
                    progress_cb(battles_done, total_battles, gen,
                                generations, max(best_score, 0.0))

            wr, score = _evaluate(w, all_moves, eval_depth, scenarios,
                                  opponent_factories,
                                  should_stop=should_stop, battle_cb=_battle_cb)
            scores.append(score)
            winrates.append(wr)

            # Mejor global incremental por fitness CONTINUO (no se pierde aunque
            # se cancele a media gen). Se guarda su win-rate para mostrar/guardar.
            if score > best_score:
                best_score   = score
                best_winrate = wr
                best_weights = w[:]

        if not scores:
            break   # cancelado antes de evaluar nada en esta generación

        actual_gens   = gen
        gen_best_cont = max(scores)
        avg_cont      = sum(scores) / len(scores)

        history.append({
            "gen":          gen,
            "best_gen":     round(gen_best_cont, 4),   # fitness continuo de la gen
            "best_global":  round(best_score, 4),      # fitness continuo (sube en la gráfica)
            "avg":          round(avg_cont, 4),
            "win_rate":     round(best_winrate, 4),    # win-rate del mejor (referencia)
            "best_weights": best_weights[:],
        })

        if callback:
            # La gráfica muestra el fitness CONTINUO (sube suave cada generación).
            callback(gen, generations, gen_best_cont, best_score,
                     avg_cont, population[:])

        # Cancelado a media generación o señal de parada: terminar aquí.
        if len(scores) < pop_size or (should_stop is not None and should_stop()):
            break

        # ── 2. Elitismo (por fitness continuo) ────────────────────────────────
        sorted_pairs = sorted(zip(scores, population), reverse=True)
        new_pop      = [ind for _, ind in sorted_pairs[:elite_k]]

        # ── 3. Reproducción ───────────────────────────────────────────────────
        while len(new_pop) < pop_size:
            p1    = _tournament(population, scores)
            p2    = _tournament(population, scores)
            child = _crossover(p1, p2)
            child = _mutate(child, mutation_rate, mutation_strength)
            new_pop.append(child)

        population = new_pop

    if best_weights is None:          # salvaguarda: nunca se evaluó nada
        best_weights = population[0][:]
        best_winrate = max(best_winrate, 0.0)
        best_score   = max(best_score, 0.0)

    return {
        "weights":           best_weights,
        "fitness":           round(best_score, 4),    # fitness continuo (lo que sube en la gráfica)
        "win_rate":          round(best_winrate, 4),  # win-rate del mejor (referencia)
        "generations":       actual_gens or generations,
        "pop_size":          pop_size,
        "battles_per_eval":  battles_per_eval,
        "minimax_depth":     minimax_depth,       # profundidad de JUEGO
        "train_depth":       eval_depth,          # profundidad de ENTRENAMIENTO
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
