"""
Experimentos para el informe de PokeFisi.
Genera tablas (stdout + JSON) y figuras (docs/informe/figs/).

Métricas: win-rate con intervalo de confianza de Wilson (95%), duración de
partidas (turnos) y tasa de empates. Ejecutar desde la raíz del repo:
    python docs/informe/run_experiments.py
"""
import os
import sys
import json
import time
import math
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from engine.loader import load_moves, load_all_pokemon, build_team
from engine.state import BattleState
from engine.battle import Battle, MAX_TURNS
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent
from ai.heuristic_improved import HeuristicImprovedAgent
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


def wilson(wins, n, z=1.96):
    """Intervalo de confianza de Wilson (95%) para una proporción, en %."""
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return (round((c - h) * 100, 1), round((c + h) * 100, 1))


def get_genetic():
    path = os.path.join("data", "genetic_g15_p12_d2.json")
    if os.path.exists(path):
        d = json.load(open(path, encoding="utf-8"))
        return d["weights"]
    d = run_genetic(pop_size=10, generations=8, battles_per_eval=15, minimax_depth=2)
    return d["weights"]


# ── Duelo con métricas ──────────────────────────────────────────────────────────

def duel(make_a, make_b, n):
    """n batallas, A alterna lados. Devuelve (wins_a, wins_b, draws, turnos_totales)."""
    wins_a = wins_b = draws = turns = 0
    for i in range(n):
        st = random_state()
        if i % 2 == 0:
            w = Battle(st, make_a(), make_b()).run()
            a_id, b_id = 1, 2
        else:
            w = Battle(st, make_b(), make_a()).run()
            a_id, b_id = 2, 1
        turns += st.turn_number
        if w == a_id:   wins_a += 1
        elif w == b_id: wins_b += 1
        else:           draws += 1
    return wins_a, wins_b, draws, turns


# ── Exp A: torneo todos contra todos ────────────────────────────────────────────

def exp_tournament(n=80):
    print(f"\n=== EXP A: Torneo ({n} batallas por par) ===")
    gw = get_genetic()
    agents = [
        ("Random",     lambda: RandomAgent()),
        ("H.Basica",   lambda: HeuristicBasicAgent()),
        ("H.Avanzada", lambda: HeuristicAdvancedAgent()),
        ("H.Mejorada", lambda: HeuristicImprovedAgent()),
        ("Minimax-d2", lambda: MinimaxAgent(depth=2)),
        ("Genetico",   lambda: GeneticAgent(weights=gw, metadata={"minimax_depth": 2})),
    ]
    names = [a[0] for a in agents]
    matrix = {a: {b: None for b in names} for a in names}
    totals = {a: [0, 0] for a in names}
    all_turns = all_draws = all_games = 0

    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            na, fa = agents[i]; nb, fb = agents[j]
            t = time.time()
            wa, wb, draws, turns = duel(fa, fb, n)
            matrix[na][nb] = round(wa / n * 100, 1)
            matrix[nb][na] = round(wb / n * 100, 1)
            totals[na][0] += wa; totals[na][1] += n
            totals[nb][0] += wb; totals[nb][1] += n
            all_turns += turns; all_draws += draws; all_games += n
            print(f"  {na:11} vs {nb:11}: {wa/n*100:5.1f}%  empates {draws:2}  "
                  f"turnos~{turns/n:4.1f}  [{time.time()-t:.0f}s]")

    overall = {a: round(totals[a][0] / totals[a][1] * 100, 1) for a in names}
    ci = {a: wilson(totals[a][0], totals[a][1]) for a in names}
    print("  Win-rate global:", overall)
    RESULTS["tournament"] = {
        "names": names, "matrix": matrix, "overall": overall, "ci": ci, "n": n,
        "avg_turns": round(all_turns / all_games, 1),
        "draw_rate": round(all_draws / all_games * 100, 1),
    }


# ── Exp B: profundidad y poda alfa-beta ────────────────────────────────────────

def exp_depth(n_pos=40, n_battles=80):
    print(f"\n=== EXP B: Profundidad minimax y poda alfa-beta ===")
    positions = [random_state() for _ in range(n_pos)]
    cost = {}
    for d in (1, 2, 3):
        np_ = pr_ = full_ = 0; ms_ = 0.0
        for st in positions:
            ag = MinimaxAgent(depth=d); ag.prune = True
            ag.choose_action(st.copy(), 1)
            s = ag.last_brain_data["stats"]
            np_ += s["nodos"]; pr_ += s["podas"]; ms_ += s["ms"]
            ag2 = MinimaxAgent(depth=d); ag2.prune = False
            ag2.choose_action(st.copy(), 1)
            full_ += ag2.last_brain_data["stats"]["nodos"]
        cost[d] = {
            "nodos_poda": round(np_ / n_pos, 1), "nodos_full": round(full_ / n_pos, 1),
            "podas": round(pr_ / n_pos, 1), "ms": round(ms_ / n_pos, 2),
            "reduccion": round((1 - np_ / full_) * 100, 1) if full_ else 0,
        }
        print(f"  d={d}: nodos(poda)={cost[d]['nodos_poda']} full={cost[d]['nodos_full']}"
              f" reduccion={cost[d]['reduccion']}% {cost[d]['ms']}ms")

    wr = {}
    for d in (1, 2, 3):
        t = time.time()
        wa, wb, draws, turns = duel(lambda d=d: MinimaxAgent(depth=d),
                                    lambda: HeuristicBasicAgent(), n_battles)
        wr[d] = {"winrate": round(wa / n_battles * 100, 1),
                 "ci": wilson(wa, n_battles),
                 "turns": round(turns / n_battles, 1)}
        print(f"  win-rate Minimax d={d} vs H.Basica: {wr[d]['winrate']}% "
              f"CI{wr[d]['ci']} turnos~{wr[d]['turns']} [{time.time()-t:.0f}s]")

    RESULTS["depth"] = {"cost": cost, "winrate_vs_basic": wr,
                        "n_pos": n_pos, "n_battles": n_battles}

    ds = [1, 2, 3]
    plt.figure(figsize=(5, 3.2))
    plt.plot(ds, [cost[d]["nodos_full"] for d in ds], "o-", label="sin poda", color="#c0504d")
    plt.plot(ds, [cost[d]["nodos_poda"] for d in ds], "s-", label="con poda α-β", color="#4f81bd")
    plt.xlabel("Profundidad"); plt.ylabel("Nodos por decisión (prom.)")
    plt.xticks(ds); plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "poda_nodos.pdf")); plt.close()


# ── Exp C: elitismo en el algoritmo genético (varias semillas) ──────────────────

def exp_elitism(pop=8, gens=8, bpe=12, depth=2, seeds=(1, 2, 3)):
    print(f"\n=== EXP C: Elitismo (pop={pop}, gen={gens}, bpe={bpe}, {len(seeds)} semillas) ===")
    avg_curves = {0: [], 2: [], 4: []}   # promedio de población por generación
    finals = {0: [], 2: [], 4: []}       # mejor fitness final por semilla
    for ek in (0, 2, 4):
        per_seed_avg = []
        for sd in seeds:
            hist_avg = []
            def cb(g, tot, bg, bgl, avg, pop_, ha=hist_avg):
                ha.append(avg)
            random.seed(sd)
            data = run_genetic(pop_size=pop, generations=gens, battles_per_eval=bpe,
                               minimax_depth=depth, elite_k=ek, callback=cb)
            per_seed_avg.append(hist_avg)
            finals[ek].append(data["fitness"])
        # promedio (entre semillas) de la curva de fitness promedio de población
        avg_curves[ek] = [sum(s[g] for s in per_seed_avg) / len(seeds)
                          for g in range(gens)]
        m = sum(finals[ek]) / len(finals[ek])
        sd_ = (sum((x - m) ** 2 for x in finals[ek]) / len(finals[ek])) ** 0.5
        print(f"  elite_k={ek}: fitness_final medio={m*100:.1f}% (±{sd_*100:.1f})")

    RESULTS["elitism"] = {
        "pop": pop, "gens": gens, "bpe": bpe, "seeds": list(seeds),
        "finals_mean": {str(k): round(sum(v) / len(v) * 100, 1) for k, v in finals.items()},
        "finals_std":  {str(k): round((sum((x - sum(v)/len(v))**2 for x in v)/len(v))**0.5 * 100, 1)
                        for k, v in finals.items()},
        "avg_curves":  {str(k): [round(x, 4) for x in v] for k, v in avg_curves.items()},
    }

    plt.figure(figsize=(5, 3.2))
    colors = {0: "#c0504d", 2: "#4f81bd", 4: "#9bbb59"}
    xs = list(range(1, gens + 1))
    for ek in (0, 2, 4):
        plt.plot(xs, [v * 100 for v in avg_curves[ek]], "o-",
                 color=colors[ek], label=f"elite_k={ek}")
    plt.xlabel("Generación"); plt.ylabel("Fitness promedio de población (%)")
    plt.ylim(0, 100); plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(os.path.join(FIGS, "elitismo_avg.pdf")); plt.close()


if __name__ == "__main__":
    t0 = time.time()
    exp_tournament(n=80)
    exp_depth(n_pos=40, n_battles=80)
    exp_elitism(pop=8, gens=8, bpe=12, seeds=(1, 2, 3))
    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=2)
    print(f"\nTOTAL: {time.time()-t0:.0f}s. Resultados en docs/informe/results.json y figs/")
