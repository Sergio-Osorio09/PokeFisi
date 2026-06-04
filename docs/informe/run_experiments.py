"""
Experimentos para el informe de PokeFisi.
Genera tablas (stdout + JSON) y figuras (docs/informe/figs/).

Ejecutar desde la raiz del repo:  python docs/informe/run_experiments.py
"""
import os
import sys
import json
import time
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from engine.loader import load_moves, load_all_pokemon, build_team
from engine.state import BattleState
from engine.battle import Battle
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent
from ai.minimax_agent import MinimaxAgent
from ai.genetic_agent import GeneticAgent
from ai.genetic_trainer import run_genetic

FIGS = os.path.join(os.path.dirname(__file__), "figs")
os.makedirs(FIGS, exist_ok=True)

MOVES = load_moves()
IDS   = [p["id"] for p in load_all_pokemon()]
RESULTS = {}


def random_state(size=3):
    return BattleState(build_team(random.sample(IDS, size), MOVES),
                       build_team(random.sample(IDS, size), MOVES))


# ── Genético: cargar/entrenar uno para el torneo ───────────────────────────────

def get_genetic():
    path = os.path.join("data", "genetic_g15_p12_d2.json")
    if os.path.exists(path):
        d = json.load(open(path, encoding="utf-8"))
        return GeneticAgent(weights=d["weights"], metadata=d)
    d = run_genetic(pop_size=10, generations=8, battles_per_eval=6, minimax_depth=2)
    return GeneticAgent(weights=d["weights"], metadata=d)


# ── Exp A: torneo todos contra todos ───────────────────────────────────────────

def duel(make_a, make_b, n):
    """n batallas; A es J1 en la mitad y J2 en la otra. Devuelve (winsA, draws)."""
    wins_a = draws = 0
    for i in range(n):
        st = random_state()
        if i % 2 == 0:
            w = Battle(st, make_a(), make_b()).run()
            if w == 1: wins_a += 1
            elif w is None: draws += 1
        else:
            w = Battle(st, make_b(), make_a()).run()
            if w == 2: wins_a += 1
            elif w is None: draws += 1
    return wins_a, draws


def exp_tournament(n=40):
    print(f"\n=== EXP A: Torneo ({n} batallas por par) ===")
    gen = get_genetic()
    agents = [
        ("Random",     lambda: RandomAgent()),
        ("H.Basica",   lambda: HeuristicBasicAgent()),
        ("H.Avanzada", lambda: HeuristicAdvancedAgent()),
        ("Minimax-d2", lambda: MinimaxAgent(depth=2)),
        ("Genetico",   lambda: GeneticAgent(weights=gen.weights,
                                            metadata={"minimax_depth": 2})),
    ]
    names = [a[0] for a in agents]
    matrix = {a: {b: None for b in names} for a in names}
    totals = {a: [0, 0] for a in names}  # [wins, games]

    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            na, fa = agents[i]
            nb, fb = agents[j]
            t = time.time()
            wa, draws = duel(fa, fb, n)
            wb = n - wa - draws
            wr_a = wa / n * 100
            matrix[na][nb] = round(wr_a, 1)
            matrix[nb][na] = round(wb / n * 100, 1)
            totals[na][0] += wa; totals[na][1] += n
            totals[nb][0] += wb; totals[nb][1] += n
            print(f"  {na:11} vs {nb:11}: {wr_a:5.1f}% (empates {draws})  [{time.time()-t:.0f}s]")

    overall = {a: round(totals[a][0] / totals[a][1] * 100, 1) for a in names}
    print("  Win-rate global:", overall)
    RESULTS["tournament"] = {"names": names, "matrix": matrix, "overall": overall, "n": n}


# ── Exp B: profundidad y poda alfa-beta ────────────────────────────────────────

def exp_depth(n_pos=40, n_battles=40):
    print(f"\n=== EXP B: Profundidad minimax y poda alfa-beta ===")

    # B1: coste de busqueda por decision y beneficio de la poda
    positions = [random_state() for _ in range(n_pos)]
    cost = {}
    for d in (1, 2, 3):
        np_, pr_, ms_, full_ = 0, 0, 0.0, 0
        for st in positions:
            ag = MinimaxAgent(depth=d)
            ag.prune = True
            ag.choose_action(st.copy(), 1)
            s = ag.last_brain_data["stats"]
            np_ += s["nodos"]; pr_ += s["podas"]; ms_ += s["ms"]
            ag2 = MinimaxAgent(depth=d); ag2.prune = False
            ag2.choose_action(st.copy(), 1)
            full_ += ag2.last_brain_data["stats"]["nodos"]
        cost[d] = {
            "nodos_poda":  round(np_ / n_pos, 1),
            "nodos_full":  round(full_ / n_pos, 1),
            "podas":       round(pr_ / n_pos, 1),
            "ms":          round(ms_ / n_pos, 2),
            "reduccion":   round((1 - np_ / full_) * 100, 1) if full_ else 0,
        }
        print(f"  d={d}: nodos(poda)={cost[d]['nodos_poda']}  nodos(full)={cost[d]['nodos_full']}"
              f"  reduccion={cost[d]['reduccion']}%  {cost[d]['ms']}ms/decision")

    # B2: win-rate vs H.Basica segun profundidad
    wr = {}
    for d in (1, 2, 3):
        t = time.time()
        wins, draws = duel(lambda d=d: MinimaxAgent(depth=d),
                           lambda: HeuristicBasicAgent(), n_battles)
        wr[d] = round(wins / n_battles * 100, 1)
        print(f"  win-rate Minimax d={d} vs H.Basica: {wr[d]}%  [{time.time()-t:.0f}s]")

    RESULTS["depth"] = {"cost": cost, "winrate_vs_basic": wr,
                        "n_pos": n_pos, "n_battles": n_battles}

    # Figura: nodos con/sin poda
    ds = [1, 2, 3]
    plt.figure(figsize=(5, 3.2))
    plt.plot(ds, [cost[d]["nodos_full"] for d in ds], "o-", label="sin poda", color="#c0504d")
    plt.plot(ds, [cost[d]["nodos_poda"] for d in ds], "s-", label="con poda α-β", color="#4f81bd")
    plt.xlabel("Profundidad"); plt.ylabel("Nodos por decisión (prom.)")
    plt.xticks(ds); plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "poda_nodos.pdf")); plt.close()


# ── Exp C: elitismo en el algoritmo genético ───────────────────────────────────

def exp_elitism(pop=12, gens=10, bpe=6, depth=2):
    print(f"\n=== EXP C: Elitismo en el AG (pop={pop}, gen={gens}) ===")
    curves = {}
    finals = {}
    for ek in (0, 2, 4):
        hist_avg, hist_best = [], []
        def cb(g, tot, bg, bgl, avg, pop_, ha=hist_avg, hb=hist_best):
            ha.append(avg); hb.append(bgl)
        t = time.time()
        random.seed(123)
        data = run_genetic(pop_size=pop, generations=gens, battles_per_eval=bpe,
                           minimax_depth=depth, elite_k=ek, callback=cb)
        curves[ek] = {"avg": hist_avg, "best": hist_best}
        finals[ek] = round(data["fitness"] * 100, 1)
        print(f"  elite_k={ek}: fitness_final={finals[ek]}%  avg_final={hist_avg[-1]*100:.1f}%"
              f"  [{time.time()-t:.0f}s]")
    RESULTS["elitism"] = {"finals": finals,
                          "curves": {str(k): v for k, v in curves.items()},
                          "pop": pop, "gens": gens, "bpe": bpe}

    # Figura: convergencia (mejor global) por elitismo
    plt.figure(figsize=(5, 3.2))
    colors = {0: "#c0504d", 2: "#4f81bd", 4: "#9bbb59"}
    xs = list(range(1, gens + 1))
    for ek in (0, 2, 4):
        plt.plot(xs, [v * 100 for v in curves[ek]["best"]], "o-",
                 color=colors[ek], label=f"elite_k={ek}")
    plt.xlabel("Generación"); plt.ylabel("Mejor fitness global (%)")
    plt.ylim(0, 105); plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "elitismo_best.pdf")); plt.close()

    # Figura: promedio de poblacion por elitismo (senal de calidad real)
    plt.figure(figsize=(5, 3.2))
    for ek in (0, 2, 4):
        plt.plot(xs, [v * 100 for v in curves[ek]["avg"]], "o-",
                 color=colors[ek], label=f"elite_k={ek}")
    plt.xlabel("Generación"); plt.ylabel("Fitness promedio de población (%)")
    plt.ylim(0, 105); plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "elitismo_avg.pdf")); plt.close()


if __name__ == "__main__":
    t0 = time.time()
    exp_tournament(n=40)
    exp_depth(n_pos=40, n_battles=40)
    exp_elitism(pop=12, gens=10, bpe=6, depth=2)
    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=2)
    print(f"\nTOTAL: {time.time()-t0:.0f}s. Resultados en docs/informe/results.json y figs/")
