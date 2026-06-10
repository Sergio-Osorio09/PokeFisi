"""
Experimentos v2 de PokeFisi: el Algoritmo Genético sobre la Heurística MEJORADA.

Cambio respecto a v1: además del genético clásico (4 pesos, evaluación Avanzada),
se entrena un genético sobre la evaluación Mejorada de 6 componentes
(superv, hp_pond, ko_threat, ko_danger, cobertura, vel) y se comparan ambos
en TODOS los experimentos.

Experimentos:
  0) Entrenamiento de ambos genéticos con receta idéntica (CRN, misma semilla).
  A) Torneo todos contra todos con 7 agentes (80 batallas/par, lados alternados).
  B) Profundidad y poda alfa-beta + coste de la evaluación 4 vs 6 componentes.
  C) Elitismo en el genético mejorado (e ∈ {0,2,4}, 3 semillas).
  D) Variantes: D1 expectimax-vs-paranoid; D2 genético-6 un rival vs panel.
  E) Refinamiento y techo: E1 robustez (inmigrantes), E2 techo 4 vs 6 pesos,
     E3 Avanzada vs Mejorada a un nivel.

Salidas (docs/informe/v2/):
  results/exp{0,A,B,C,D,E}_*.json   — un JSON ordenado por experimento
  results/results_v2.json           — todo combinado
  figs/*.png y *.pdf                — al menos un gráfico por experimento

Ejecutar desde la raíz del repo:  python docs/informe/v2/run_experiments_v2.py
"""
import os
import sys
import json
import time
import math
import random
import statistics

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from engine.loader import load_moves, load_all_pokemon, build_team
from engine.state import BattleState
from engine.battle import Battle
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent
from ai.heuristic_improved import HeuristicImprovedAgent
from ai.minimax_agent import MinimaxAgent
from ai.minimax_improved_agent import MinimaxImprovedAgent
from ai.expectimax_agent import ExpectimaxAgent
from ai.genetic_agent import GeneticAgent, GeneticImprovedAgent
from ai.genetic_trainer import run_genetic, save_genetic_weights

BASE    = os.path.dirname(__file__)
FIGS    = os.path.join(BASE, "figs")
RESULTS = os.path.join(BASE, "results")
os.makedirs(FIGS, exist_ok=True)
os.makedirs(RESULTS, exist_ok=True)

MOVES = load_moves()
IDS   = [p["id"] for p in load_all_pokemon()]
PANEL = [RandomAgent, HeuristicBasicAgent, HeuristicAdvancedAgent]
ALL   = {}

# Receta de entrenamiento refinada (Experimento E del informe v1).
TRAIN_CFG = dict(pop_size=16, generations=15, battles_per_eval=24,
                 minimax_depth=2, train_depth=1,
                 immigrants=2, truncation=0.40,
                 mutation_rate=0.20, mutation_strength=0.15)
TRAIN_SEED = 3


def log(msg):
    print(msg, flush=True)


def save_json(name, payload):
    path = os.path.join(RESULTS, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    log(f"  -> guardado {os.path.relpath(path, BASE)}")


def savefig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIGS, name + ".png"), dpi=150)
    plt.savefig(os.path.join(FIGS, name + ".pdf"))
    plt.close()
    log(f"  -> figura {name}.png/.pdf")


def random_state(size=3):
    return BattleState(build_team(random.sample(IDS, size), MOVES),
                       build_team(random.sample(IDS, size), MOVES))


def wilson(wins, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return (round((c - h) * 100, 1), round((c + h) * 100, 1))


def duel(make_a, make_b, n):
    """n batallas, A alterna lados. Devuelve (wins_a, wins_b, draws, turnos)."""
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
        if w == a_id:
            wins_a += 1
        elif w == b_id:
            wins_b += 1
        else:
            draws += 1
    return wins_a, wins_b, draws, turns


def duel_fixed(make_a, make_b, n, seed0):
    """Win-rate (%) de A (jugador 1) vs B en n escenarios fijos (CRN)."""
    random.seed(seed0)
    scen = [(random.sample(IDS, 3), random.sample(IDS, 3)) for _ in range(n)]
    wa = 0
    for ids1, ids2 in scen:
        st = BattleState(build_team(ids1, MOVES), build_team(ids2, MOVES))
        if Battle(st, make_a(), make_b()).run() == 1:
            wa += 1
    return round(wa / n * 100, 1)


def wr_vs_panel(weights, depth, n, agent_class=MinimaxAgent, seed0=777):
    """Win-rate (%) de agent_class(depth, weights) contra el panel en n
    escenarios FIJOS (mismos para cualquier vector -> comparación justa)."""
    random.seed(seed0)
    scen = [(random.sample(IDS, 3), random.sample(IDS, 3),
             random.randrange(2 ** 31), i % len(PANEL)) for i in range(n)]
    wins = 0
    for ids1, ids2, seed, oi in scen:
        random.seed(seed)
        opp = PANEL[oi]()
        st  = BattleState(build_team(ids1, MOVES), build_team(ids2, MOVES))
        if Battle(st, agent_class(depth=depth, weights=weights), opp).run() == 1:
            wins += 1
    return round(wins / n * 100, 1)


def bench_ms(make_agent, k=120):
    """Tiempo medio por decisión (ms) sobre k estados aleatorios."""
    ag = make_agent()
    t  = 0.0
    for _ in range(k):
        st = random_state()
        t0 = time.perf_counter()
        ag.choose_action(st, 1)
        t += time.perf_counter() - t0
    return round(t / k * 1000, 2)


# ══ EXP 0: entrenamiento de ambos genéticos (receta idéntica, CRN) ═════════════

def exp0_entrenamiento():
    log("\n=== EXP 0: entrenamiento de los genéticos (4 vs 6 pesos) ===")
    log(f"  receta: {TRAIN_CFG}  panel={[c().name for c in PANEL]}  seed={TRAIN_SEED}")

    t0 = time.time()
    random.seed(TRAIN_SEED)
    g4 = run_genetic(**TRAIN_CFG, opponent_factories=PANEL)
    t4 = time.time() - t0
    log(f"  AG-4 (avanzada)  pesos={[round(x,3) for x in g4['weights']]}  "
        f"win_rate_train={g4['win_rate']:.1%}  [{t4:.0f}s]")

    t0 = time.time()
    random.seed(TRAIN_SEED)
    g6 = run_genetic(**TRAIN_CFG, opponent_factories=PANEL,
                     agent_class=MinimaxImprovedAgent)
    t6 = time.time() - t0
    log(f"  AG-6 (mejorada)  pesos={[round(x,3) for x in g6['weights']]}  "
        f"win_rate_train={g6['win_rate']:.1%}  [{t6:.0f}s]")

    p4 = save_genetic_weights(g4)
    p6 = save_genetic_weights(g6)
    log(f"  pesos guardados en {p4} y {p6}")

    ALL["exp0"] = {
        "config": {**TRAIN_CFG, "seed": TRAIN_SEED,
                   "panel": [c().name for c in PANEL]},
        "ag4": {"weights": [round(x, 4) for x in g4["weights"]],
                "labels": ["supervivencia", "hp_diff", "tipo", "velocidad"],
                "win_rate_train": g4["win_rate"], "fitness": g4["fitness"],
                "history": g4["history"], "train_seconds": round(t4, 1),
                "weights_file": p4},
        "ag6": {"weights": [round(x, 4) for x in g6["weights"]],
                "labels": ["superv", "hp_pond", "ko_threat", "ko_danger",
                            "cobertura", "velocidad"],
                "win_rate_train": g6["win_rate"], "fitness": g6["fitness"],
                "history": g6["history"], "train_seconds": round(t6, 1),
                "weights_file": p6},
    }
    save_json("exp0_entrenamiento.json", ALL["exp0"])

    # Figura: curvas de fitness por generación (mejor global y promedio).
    plt.figure(figsize=(6, 3.6))
    for tag, g, c in (("AG-4 (Avanzada)", g4, "#4f81bd"),
                      ("AG-6 (Mejorada)", g6, "#c0504d")):
        xs = [h["gen"] for h in g["history"]]
        plt.plot(xs, [h["best_global"] * 100 for h in g["history"]], "-o",
                 color=c, label=f"{tag}: mejor global")
        plt.plot(xs, [h["avg"] * 100 for h in g["history"]], "--",
                 color=c, alpha=0.5, label=f"{tag}: promedio")
    plt.xlabel("Generación")
    plt.ylabel("Fitness continuo (%)")
    plt.legend(fontsize=7)
    plt.grid(alpha=0.3)
    savefig("exp0_fitness")

    return g4["weights"], g6["weights"]


# ══ EXP A: torneo todos contra todos (7 agentes) ═══════════════════════════════

def expA_torneo(w4, w6, n=80):
    log(f"\n=== EXP A: torneo de 7 agentes ({n} batallas por par) ===")
    random.seed(101)
    agents = [
        ("Random",      lambda: RandomAgent()),
        ("H.Basica",    lambda: HeuristicBasicAgent()),
        ("H.Avanzada",  lambda: HeuristicAdvancedAgent()),
        ("H.Mejorada",  lambda: HeuristicImprovedAgent()),
        ("Minimax-d2",  lambda: MinimaxAgent(depth=2)),
        ("Genetico-4",  lambda: GeneticAgent(weights=w4, metadata={"minimax_depth": 2})),
        ("Genetico-6",  lambda: GeneticImprovedAgent(weights=w6, metadata={"minimax_depth": 2})),
    ]
    names  = [a[0] for a in agents]
    matrix = {a: {b: None for b in names} for a in names}
    totals = {a: [0, 0] for a in names}
    all_turns = all_draws = all_games = 0

    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            na, fa = agents[i]
            nb, fb = agents[j]
            t = time.time()
            wa, wb, draws, turns = duel(fa, fb, n)
            matrix[na][nb] = round(wa / n * 100, 1)
            matrix[nb][na] = round(wb / n * 100, 1)
            totals[na][0] += wa
            totals[na][1] += n
            totals[nb][0] += wb
            totals[nb][1] += n
            all_turns += turns
            all_draws += draws
            all_games += n
            log(f"  {na:11} vs {nb:11}: {wa/n*100:5.1f}%  empates {draws:2}  "
                f"turnos~{turns/n:4.1f}  [{time.time()-t:.0f}s]")

    overall = {a: round(totals[a][0] / totals[a][1] * 100, 1) for a in names}
    ci      = {a: wilson(totals[a][0], totals[a][1]) for a in names}
    log(f"  Win-rate global: {overall}")

    ALL["expA"] = {
        "names": names, "matrix": matrix, "overall": overall, "ci": ci, "n": n,
        "avg_turns": round(all_turns / all_games, 1),
        "draw_rate": round(all_draws / all_games * 100, 1),
        "weights_used": {"genetico4": [round(x, 4) for x in w4],
                         "genetico6": [round(x, 4) for x in w6]},
    }
    save_json("expA_torneo.json", ALL["expA"])

    # Figura: win-rate global con IC de Wilson.
    order  = sorted(names, key=lambda a: overall[a])
    vals   = [overall[a] for a in order]
    lo     = [overall[a] - ci[a][0] for a in order]
    hi     = [ci[a][1] - overall[a] for a in order]
    colors = ["#c0504d" if "Genetico-6" in a else
              "#e8a33d" if "Genetico-4" in a else "#4f81bd" for a in order]
    plt.figure(figsize=(6, 3.6))
    plt.barh(order, vals, xerr=[lo, hi], color=colors, capsize=3)
    plt.axvline(50, color="gray", ls="--", lw=0.8)
    plt.xlabel("Win-rate global (%) — IC 95% Wilson")
    plt.grid(alpha=0.3, axis="x")
    savefig("expA_torneo")


# ══ EXP B: profundidad, poda y coste de la evaluación 4 vs 6 ═══════════════════

def expB_profundidad(n_pos=40, n_battles=80):
    log("\n=== EXP B: profundidad, poda alfa-beta y coste 4 vs 6 componentes ===")
    random.seed(202)
    positions = [random_state() for _ in range(n_pos)]

    cost = {}
    for d in (1, 2, 3):
        np_ = pr_ = full_ = 0
        ms_adv = ms_imp = 0.0
        for st in positions:
            ag = MinimaxAgent(depth=d)
            ag.prune = True
            ag.choose_action(st.copy(), 1)
            s = ag.last_brain_data["stats"]
            np_ += s["nodos"]
            pr_ += s["podas"]
            ms_adv += s["ms"]

            ag2 = MinimaxAgent(depth=d)
            ag2.prune = False
            ag2.choose_action(st.copy(), 1)
            full_ += ag2.last_brain_data["stats"]["nodos"]

            ag3 = MinimaxImprovedAgent(depth=d)
            ag3.choose_action(st.copy(), 1)
            ms_imp += ag3.last_brain_data["stats"]["ms"]

        cost[d] = {
            "nodos_poda": round(np_ / n_pos, 1),
            "nodos_full": round(full_ / n_pos, 1),
            "podas":      round(pr_ / n_pos, 1),
            "reduccion":  round((1 - np_ / full_) * 100, 1) if full_ else 0,
            "ms_eval4":   round(ms_adv / n_pos, 2),
            "ms_eval6":   round(ms_imp / n_pos, 2),
        }
        log(f"  d={d}: nodos(poda)={cost[d]['nodos_poda']} full={cost[d]['nodos_full']} "
            f"reduccion={cost[d]['reduccion']}%  ms eval4={cost[d]['ms_eval4']} "
            f"eval6={cost[d]['ms_eval6']}")

    wr = {}
    for d in (1, 2, 3):
        t = time.time()
        wa, wb, draws, turns = duel(lambda d=d: MinimaxAgent(depth=d),
                                    lambda: HeuristicBasicAgent(), n_battles)
        wr[d] = {"winrate": round(wa / n_battles * 100, 1),
                 "ci": wilson(wa, n_battles),
                 "turns": round(turns / n_battles, 1)}
        log(f"  win-rate Minimax d={d} vs H.Basica: {wr[d]['winrate']}% "
            f"CI{wr[d]['ci']} turnos~{wr[d]['turns']} [{time.time()-t:.0f}s]")

    ALL["expB"] = {"cost": cost, "winrate_vs_basic": wr,
                   "n_pos": n_pos, "n_battles": n_battles}
    save_json("expB_profundidad.json", ALL["expB"])

    ds = [1, 2, 3]
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.4))
    axes[0].plot(ds, [cost[d]["nodos_full"] for d in ds], "o-",
                 label="sin poda", color="#c0504d")
    axes[0].plot(ds, [cost[d]["nodos_poda"] for d in ds], "s-",
                 label="con poda α-β", color="#4f81bd")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("Profundidad")
    axes[0].set_ylabel("Nodos por decisión (log)")
    axes[0].set_xticks(ds)
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    width = 0.35
    axes[1].bar([d - width / 2 for d in ds], [cost[d]["ms_eval4"] for d in ds],
                width, label="eval 4 comp. (Avanzada)", color="#4f81bd")
    axes[1].bar([d + width / 2 for d in ds], [cost[d]["ms_eval6"] for d in ds],
                width, label="eval 6 comp. (Mejorada)", color="#c0504d")
    axes[1].set_xlabel("Profundidad")
    axes[1].set_ylabel("ms por decisión")
    axes[1].set_xticks(ds)
    axes[1].legend()
    axes[1].grid(alpha=0.3, axis="y")
    savefig("expB_poda_coste")


# ══ EXP C: elitismo en el genético MEJORADO ════════════════════════════════════

def expC_elitismo(pop=8, gens=8, bpe=12, seeds=(1, 2, 3)):
    log(f"\n=== EXP C: elitismo en el AG-6 (pop={pop}, gen={gens}, bpe={bpe}, "
        f"{len(seeds)} semillas, train_depth=1) ===")
    avg_curves = {0: [], 2: [], 4: []}
    finals     = {0: [], 2: [], 4: []}
    for ek in (0, 2, 4):
        per_seed_avg = []
        for sd in seeds:
            hist_avg = []

            def cb(g, tot, bg, bgl, avg, pop_, ha=hist_avg):
                ha.append(avg)

            random.seed(sd)
            data = run_genetic(pop_size=pop, generations=gens,
                               battles_per_eval=bpe, minimax_depth=2,
                               train_depth=1, elite_k=ek,
                               agent_class=MinimaxImprovedAgent,
                               opponent_factories=PANEL, callback=cb)
            per_seed_avg.append(hist_avg)
            finals[ek].append(data["fitness"])
        avg_curves[ek] = [sum(s[g] for s in per_seed_avg) / len(seeds)
                          for g in range(gens)]
        m   = statistics.mean(finals[ek])
        sd_ = statistics.pstdev(finals[ek])
        log(f"  elite_k={ek}: fitness_final medio={m*100:.1f}% (±{sd_*100:.1f})")

    ALL["expC"] = {
        "pop": pop, "gens": gens, "bpe": bpe, "seeds": list(seeds),
        "train_depth": 1, "panel": [c().name for c in PANEL],
        "evaluacion": "mejorada-6",
        "finals_mean": {str(k): round(statistics.mean(v) * 100, 1)
                        for k, v in finals.items()},
        "finals_std":  {str(k): round(statistics.pstdev(v) * 100, 1)
                        for k, v in finals.items()},
        "avg_curves":  {str(k): [round(x, 4) for x in v]
                        for k, v in avg_curves.items()},
    }
    save_json("expC_elitismo.json", ALL["expC"])

    plt.figure(figsize=(5.5, 3.4))
    colors = {0: "#c0504d", 2: "#4f81bd", 4: "#9bbb59"}
    xs = list(range(1, gens + 1))
    for ek in (0, 2, 4):
        plt.plot(xs, [v * 100 for v in avg_curves[ek]], "o-",
                 color=colors[ek], label=f"elite_k={ek}")
    plt.xlabel("Generación")
    plt.ylabel("Fitness promedio de población (%)")
    plt.legend()
    plt.grid(alpha=0.3)
    savefig("expC_elitismo")


# ══ EXP D: variantes (D1 expectimax; D2 genético-6 single vs panel) ════════════

def _winrates_vs(make_agent, panel, n):
    res   = {}
    tot_w = tot_n = 0
    for nm, fb in panel:
        w = 0
        for i in range(n):
            st = random_state()
            if i % 2 == 0:
                w += (Battle(st, make_agent(), fb()).run() == 1)
            else:
                w += (Battle(st, fb(), make_agent()).run() == 2)
        res[nm] = round(w / n * 100, 1)
        tot_w += w
        tot_n += n
    res["GLOBAL"] = round(tot_w / tot_n * 100, 1)
    res["CI"]     = wilson(tot_w, tot_n)
    return res


def expD_variantes(n=60, pop=10, gens=10, bpe=15):
    log(f"\n=== EXP D: variantes ===")
    random.seed(404)
    panel3 = [("Random",   lambda: RandomAgent()),
              ("Basica",   lambda: HeuristicBasicAgent()),
              ("Avanzada", lambda: HeuristicAdvancedAgent())]

    # D1: expectimax-contra-modelo vs minimax paranoid.
    log(f"  D1: Expectimax vs Minimax paranoid ({n} batallas/rival)")
    mmx = _winrates_vs(lambda: MinimaxAgent(depth=2), panel3, n)
    exm = _winrates_vs(lambda: ExpectimaxAgent(depth=2), panel3, n)
    wa, wb, _, _ = duel(lambda: ExpectimaxAgent(depth=2),
                        lambda: MinimaxAgent(depth=2), n)
    h2h = round(wa / n * 100, 1)
    log(f"    Minimax-d2    vs panel: {mmx}")
    log(f"    Expectimax-d2 vs panel: {exm}")
    log(f"    Expectimax vs Minimax (directo): {h2h}%")

    # D2: genético-6 entrenado contra UN rival vs contra el PANEL.
    log(f"  D2: AG-6 un rival vs panel (pop={pop} gens={gens} bpe={bpe}, train_depth=1)")
    random.seed(7)
    g_single = run_genetic(pop_size=pop, generations=gens, battles_per_eval=bpe,
                           minimax_depth=2, train_depth=1,
                           agent_class=MinimaxImprovedAgent,
                           opponent_factories=[HeuristicBasicAgent])
    random.seed(7)
    g_multi = run_genetic(pop_size=pop, generations=gens, battles_per_eval=bpe,
                          minimax_depth=2, train_depth=1,
                          agent_class=MinimaxImprovedAgent,
                          opponent_factories=PANEL)
    log(f"    pesos single: {[round(x,2) for x in g_single['weights']]}")
    log(f"    pesos multi : {[round(x,2) for x in g_multi['weights']]}")

    eval_panel = panel3 + [("Minimax-d2", lambda: MinimaxAgent(depth=2))]
    ws = _winrates_vs(lambda: GeneticImprovedAgent(
        weights=g_single["weights"], metadata={"minimax_depth": 2}), eval_panel, n)
    wm = _winrates_vs(lambda: GeneticImprovedAgent(
        weights=g_multi["weights"], metadata={"minimax_depth": 2}), eval_panel, n)
    log(f"    AG-6 SINGLE vs panel: {ws}")
    log(f"    AG-6 MULTI  vs panel: {wm}")

    ALL["expD"] = {
        "D1": {"minimax": mmx, "expectimax": exm,
               "expectimax_vs_minimax": h2h, "n": n},
        "D2": {"weights_single": [round(x, 3) for x in g_single["weights"]],
               "weights_multi":  [round(x, 3) for x in g_multi["weights"]],
               "single": ws, "multi": wm, "n": n,
               "train": {"pop": pop, "gens": gens, "bpe": bpe,
                          "train_depth": 1, "evaluacion": "mejorada-6"}},
    }
    save_json("expD_variantes.json", ALL["expD"])

    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.4))
    rivals = ["Random", "Basica", "Avanzada"]
    x = range(len(rivals))
    width = 0.35
    axes[0].bar([i - width / 2 for i in x], [mmx[r] for r in rivals],
                width, label="Minimax (paranoid)", color="#4f81bd")
    axes[0].bar([i + width / 2 for i in x], [exm[r] for r in rivals],
                width, label="Expectimax (modelo)", color="#9bbb59")
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(rivals)
    axes[0].axhline(50, color="gray", ls="--", lw=0.8)
    axes[0].set_ylabel("Win-rate (%)")
    axes[0].set_title("D1: paranoid vs modelo", fontsize=9)
    axes[0].legend(fontsize=7)
    axes[0].grid(alpha=0.3, axis="y")

    rivals2 = ["Random", "Basica", "Avanzada", "Minimax-d2"]
    x2 = range(len(rivals2))
    axes[1].bar([i - width / 2 for i in x2], [ws[r] for r in rivals2],
                width, label="fitness vs 1 rival", color="#c0504d")
    axes[1].bar([i + width / 2 for i in x2], [wm[r] for r in rivals2],
                width, label="fitness vs panel", color="#4f81bd")
    axes[1].set_xticks(list(x2))
    axes[1].set_xticklabels(rivals2, fontsize=8)
    axes[1].axhline(50, color="gray", ls="--", lw=0.8)
    axes[1].set_ylabel("Win-rate (%)")
    axes[1].set_title("D2: generalización del AG-6", fontsize=9)
    axes[1].legend(fontsize=7)
    axes[1].grid(alpha=0.3, axis="y")
    savefig("expD_variantes")


# ══ EXP E: refinamiento y techo (4 vs 6 pesos) ═════════════════════════════════

def expE_techo(w4, w6, runs=5, n_test=150):
    log("\n=== EXP E: refinamiento y techo de la evaluación ===")

    # E1: robustez del AG-6 (inmigrantes elevan el piso).
    log(f"  E1: robustez del AG-6 ({runs} corridas por configuración)")

    def run_set(**kw):
        res = []
        for _ in range(runs):
            d = run_genetic(pop_size=14, generations=12, battles_per_eval=24,
                            minimax_depth=1, train_depth=1,
                            agent_class=MinimaxImprovedAgent,
                            opponent_factories=PANEL, **kw)
            res.append(wr_vs_panel(d["weights"], 1, n_test,
                                   agent_class=MinimaxImprovedAgent))
        return res

    random.seed(1)
    sin = run_set(immigrants=0, mutation_rate=0.15, mutation_strength=0.10,
                  truncation=1.0)
    con = run_set(immigrants=2, mutation_rate=0.20, mutation_strength=0.15,
                  truncation=0.40)

    def summ(r):
        return {"runs": r, "min": min(r),
                "mean": round(statistics.mean(r), 1), "max": max(r)}

    e1 = {"sin_inmigrantes": summ(sin), "con_inmigrantes": summ(con),
          "n_test": n_test}
    log(f"    sin inmigrantes: {e1['sin_inmigrantes']}")
    log(f"    con inmigrantes: {e1['con_inmigrantes']}")

    # E2: techo de la evaluación — 4 pesos vs 6 pesos, mismos 150 escenarios.
    log("  E2: techo de la evaluación (4 vs 6 pesos, mismos escenarios)")
    configs = [
        ("default-4",     [0.40, 0.35, 0.15, 0.10],            MinimaxAgent),
        ("genetico-4",    w4,                                   MinimaxAgent),
        ("soloHP-4",      [0.0, 1.0, 0.0, 0.0],                MinimaxAgent),
        ("default-6",     [0.25, 0.20, 0.20, 0.15, 0.10, 0.10], MinimaxImprovedAgent),
        ("genetico-6",    w6,                                   MinimaxImprovedAgent),
        ("soloHP-6",      [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],      MinimaxImprovedAgent),
    ]
    table = {}
    for name, w, cls in configs:
        table[name] = {
            "weights": [round(x, 3) for x in w],
            "d1": wr_vs_panel(w, 1, n_test, agent_class=cls),
            "d2": wr_vs_panel(w, 2, n_test, agent_class=cls),
        }
        log(f"    {name:12} d1={table[name]['d1']}%  d2={table[name]['d2']}%  "
            f"{table[name]['weights']}")

    # E3: Avanzada (4) vs Mejorada (6) a un nivel + coste por decisión.
    log(f"  E3: Avanzada vs Mejorada a 1 nivel ({n_test} batallas)")
    Avz, Mej = HeuristicAdvancedAgent, HeuristicImprovedAgent
    Bas, Rnd = HeuristicBasicAgent, RandomAgent
    e3 = {
        "avanzada": {"vs_basica": duel_fixed(Avz, Bas, n_test, 42),
                     "vs_random": duel_fixed(Avz, Rnd, n_test, 43),
                     "ms_dec": bench_ms(Avz)},
        "mejorada": {"vs_basica": duel_fixed(Mej, Bas, n_test, 42),
                     "vs_random": duel_fixed(Mej, Rnd, n_test, 43),
                     "ms_dec": bench_ms(Mej)},
        "mejorada_vs_avanzada_h2h": duel_fixed(Mej, Avz, n_test, 44),
        "n": n_test,
    }
    log(f"    Avanzada: {e3['avanzada']}")
    log(f"    Mejorada: {e3['mejorada']}")
    log(f"    Mejorada vs Avanzada (directo): {e3['mejorada_vs_avanzada_h2h']}%")

    ALL["expE"] = {"E1_robustez": e1, "E2_techo": {"n_test": n_test, **table},
                   "E3_avanzada_vs_mejorada": e3}
    save_json("expE_techo.json", ALL["expE"])

    # Figura: el techo, 4 vs 6 pesos (la pregunta central del experimento).
    names = [c[0] for c in configs]
    d1v   = [table[nm]["d1"] for nm in names]
    d2v   = [table[nm]["d2"] for nm in names]
    x     = range(len(names))
    width = 0.35
    plt.figure(figsize=(7, 3.6))
    plt.bar([i - width / 2 for i in x], d1v, width, label="d=1", color="#4f81bd")
    plt.bar([i + width / 2 for i in x], d2v, width, label="d=2", color="#c0504d")
    plt.axhline(64, color="gray", ls="--", lw=1, label="techo v1 (~64%)")
    plt.xticks(list(x), names, fontsize=8)
    plt.ylabel("Win-rate vs panel (%)")
    plt.legend(fontsize=8)
    plt.grid(alpha=0.3, axis="y")
    savefig("expE_techo")


# ══ Main ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    t0 = time.time()
    w4, w6 = exp0_entrenamiento()
    expA_torneo(w4, w6, n=80)
    expB_profundidad(n_pos=40, n_battles=80)
    expC_elitismo(pop=8, gens=8, bpe=12, seeds=(1, 2, 3))
    expD_variantes(n=60)
    expE_techo(w4, w6, runs=5, n_test=150)

    save_json("results_v2.json", ALL)
    log(f"\nTOTAL: {(time.time()-t0)/60:.1f} min. "
        f"Resultados en docs/informe/v2/results/ y figs/")
