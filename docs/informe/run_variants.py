"""
Experimento D (Prioridad 3): variantes de mejora.
  D1) Expectimax-vs-modelo frente al Minimax paranoid y a las heurísticas.
  D2) Genético entrenado contra UN rival (Básica) vs contra un PANEL de rivales,
      evaluando la generalización en un mini-torneo.
Resultados -> docs/informe/results_variants.json
"""
import os, sys, json, time, math, random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from engine.loader import load_moves, load_all_pokemon, build_team
from engine.state import BattleState
from engine.battle import Battle
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent
from ai.minimax_agent import MinimaxAgent
from ai.expectimax_agent import ExpectimaxAgent
from ai.genetic_agent import GeneticAgent
from ai.genetic_trainer import run_genetic

MOVES = load_moves()
IDS   = [p["id"] for p in load_all_pokemon()]
OUT   = {}


def rstate():
    return BattleState(build_team(random.sample(IDS, 3), MOVES),
                       build_team(random.sample(IDS, 3), MOVES))


def wilson(w, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = w / n; d = 1 + z*z/n
    c = (p + z*z/(2*n))/d; h = (z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)))/d
    return (round((c-h)*100, 1), round((c+h)*100, 1))


def duel(make_a, make_b, n):
    wa = 0
    for i in range(n):
        st = rstate()
        if i % 2 == 0:
            wa += (Battle(st, make_a(), make_b()).run() == 1)
        else:
            wa += (Battle(st, make_b(), make_a()).run() == 2)
    return wa


def winrates_vs(make_agent, panel, n):
    """Win-rate del agente contra cada rival del panel (lista de (nombre, factory))."""
    res = {}
    tot_w = tot_n = 0
    for nm, fb in panel:
        w = duel(make_agent, fb, n)
        res[nm] = round(w / n * 100, 1)
        tot_w += w; tot_n += n
    res["GLOBAL"] = round(tot_w / tot_n * 100, 1)
    res["CI"] = wilson(tot_w, tot_n)
    return res


# ── D1: Expectimax vs paranoid ─────────────────────────────────────────────────

def exp_variants(n=60):
    print(f"\n=== D1: Expectimax vs Minimax paranoid ({n} batallas) ===")
    panel = [("Random", lambda: RandomAgent()),
             ("Basica", lambda: HeuristicBasicAgent()),
             ("Avanzada", lambda: HeuristicAdvancedAgent())]
    mmx = winrates_vs(lambda: MinimaxAgent(depth=2), panel, n)
    exm = winrates_vs(lambda: ExpectimaxAgent(depth=2), panel, n)
    h2h = round(duel(lambda: ExpectimaxAgent(depth=2),
                     lambda: MinimaxAgent(depth=2), n) / n * 100, 1)
    print("  Minimax-d2   vs panel:", mmx)
    print("  Expectimax-d2 vs panel:", exm)
    print(f"  Expectimax vs Minimax (directo): {h2h}%")
    OUT["variants_search"] = {"minimax": mmx, "expectimax": exm,
                              "expectimax_vs_minimax": h2h, "n": n}


# ── D2: genético un rival vs panel de rivales ──────────────────────────────────

def exp_genetic_panel(pop=10, gens=10, bpe=15, depth=2, n=60):
    print(f"\n=== D2: Genetico 1-rival vs multi-rival (train pop={pop} gen={gens}) ===")
    panel_full = [RandomAgent, HeuristicBasicAgent, HeuristicAdvancedAgent]

    random.seed(7)
    g_single = run_genetic(pop_size=pop, generations=gens, battles_per_eval=bpe,
                           minimax_depth=depth, opponent_factories=[HeuristicBasicAgent])
    random.seed(7)
    g_multi = run_genetic(pop_size=pop, generations=gens, battles_per_eval=bpe,
                          minimax_depth=depth, opponent_factories=panel_full)
    print(f"  pesos single: {[round(x,2) for x in g_single['weights']]}")
    print(f"  pesos multi : {[round(x,2) for x in g_multi['weights']]}")

    eval_panel = [("Random", lambda: RandomAgent()),
                  ("Basica", lambda: HeuristicBasicAgent()),
                  ("Avanzada", lambda: HeuristicAdvancedAgent()),
                  ("Minimax-d2", lambda: MinimaxAgent(depth=2))]
    ws = winrates_vs(lambda: GeneticAgent(weights=g_single["weights"],
                                          metadata={"minimax_depth": depth}), eval_panel, n)
    wm = winrates_vs(lambda: GeneticAgent(weights=g_multi["weights"],
                                          metadata={"minimax_depth": depth}), eval_panel, n)
    print("  Genetico SINGLE-rival vs panel:", ws)
    print("  Genetico MULTI-rival  vs panel:", wm)
    OUT["genetic_panel"] = {
        "weights_single": [round(x, 3) for x in g_single["weights"]],
        "weights_multi":  [round(x, 3) for x in g_multi["weights"]],
        "single": ws, "multi": wm, "n": n,
        "train": {"pop": pop, "gens": gens, "bpe": bpe},
    }


if __name__ == "__main__":
    t0 = time.time()
    exp_variants(n=60)
    exp_genetic_panel(pop=10, gens=10, bpe=15, n=60)
    json.dump(OUT, open(os.path.join(os.path.dirname(__file__), "results_variants.json"),
                        "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nTOTAL: {time.time()-t0:.0f}s -> results_variants.json")
