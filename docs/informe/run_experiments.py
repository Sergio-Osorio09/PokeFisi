"""
Experimentos del informe de PokeFisi (cinco experimentos seleccionados).

Cada experimento evidencia un patrón claro y genera al menos una figura. El
algoritmo genético se evalúa en dos variantes ---Genético-4 (evoluciona los 4
pesos de la evaluación avanzada) y Genético-6 (evoluciona los 6 de la mejorada)---
para poder compararlas.

  A) Torneo todos contra todos (7 agentes): jerarquía de los agentes.
  B) Poda alfa-beta: coste de búsqueda con y sin poda, y coste 4 vs 6 componentes.
  C) Profundidad y calidad: ¿mirar más turnos mejora el win-rate?
  D) Sobreajuste del genético: fitness contra un rival vs contra un panel.
  E) Techo de la evaluación: cuatro vs seis componentes (la mejor evaluación).

Salidas:
  docs/informe/results/*.json   — un JSON ordenado por experimento
  docs/informe/figs/*.{png,pdf} — una figura por experimento

Métricas: win-rate con intervalo de Wilson al 95%, lados alternados, y Common
Random Numbers (escenarios fijos) en las comparaciones de pesos. Todas las cifras
provienen de ejecuciones reales del sistema.

Ejecutar desde la raíz del repo:  python docs/informe/run_experiments.py
"""
import os
import sys
import json
import time
import math
import random
import statistics

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
from ai.heuristic_improved import HeuristicImprovedAgent
from ai.minimax_agent import MinimaxAgent
from ai.minimax_improved_agent import MinimaxImprovedAgent
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

# Receta de entrenamiento refinada (desacople de profundidad, fitness continuo,
# escenarios fijos, inmigrantes y truncamiento). Idéntica para ambos genéticos.
TRAIN_CFG  = dict(pop_size=16, generations=15, battles_per_eval=24,
                  minimax_depth=2, train_depth=1,
                  immigrants=2, truncation=0.40,
                  mutation_rate=0.20, mutation_strength=0.15)
TRAIN_SEED = 3


# ── utilidades ──────────────────────────────────────────────────────────────────

def log(msg):
    print(msg, flush=True)


def save_json(name, payload):
    path = os.path.join(RESULTS, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    log(f"  -> {os.path.relpath(path, BASE)}")


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
            w = Battle(st, make_a(), make_b()).run(); a_id, b_id = 1, 2
        else:
            w = Battle(st, make_b(), make_a()).run(); a_id, b_id = 2, 1
        turns += st.turn_number
        if w == a_id:   wins_a += 1
        elif w == b_id: wins_b += 1
        else:           draws += 1
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
    """Win-rate (%) de agent_class(depth, weights) contra el panel en n escenarios
    FIJOS (mismos para cualquier vector de pesos -> comparación justa)."""
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
    ag = make_agent(); t = 0.0
    for _ in range(k):
        st = random_state()
        t0 = time.perf_counter(); ag.choose_action(st, 1); t += time.perf_counter() - t0
    return round(t / k * 1000, 2)


# ══ Entrenamiento de los dos genéticos (receta idéntica, CRN) ════════════════════

def train_genetics():
    log("\n=== Entrenamiento de los genéticos (4 vs 6 pesos) ===")
    t = time.time(); random.seed(TRAIN_SEED)
    g4 = run_genetic(**TRAIN_CFG, opponent_factories=PANEL)
    log(f"  AG-4 pesos={[round(x,3) for x in g4['weights']]} "
        f"wr_train={g4['win_rate']:.1%} [{time.time()-t:.0f}s]")
    t = time.time(); random.seed(TRAIN_SEED)
    g6 = run_genetic(**TRAIN_CFG, opponent_factories=PANEL,
                     agent_class=MinimaxImprovedAgent)
    log(f"  AG-6 pesos={[round(x,3) for x in g6['weights']]} "
        f"wr_train={g6['win_rate']:.1%} [{time.time()-t:.0f}s]")
    save_genetic_weights(g4)
    save_genetic_weights(g6)
    ALL["entrenamiento"] = {
        "config": {**TRAIN_CFG, "seed": TRAIN_SEED},
        "ag4": {"weights": [round(x, 4) for x in g4["weights"]], "wr_train": g4["win_rate"]},
        "ag6": {"weights": [round(x, 4) for x in g6["weights"]], "wr_train": g6["win_rate"]},
    }
    save_json("entrenamiento.json", ALL["entrenamiento"])
    return g4["weights"], g6["weights"]


# ══ A. Torneo todos contra todos ═════════════════════════════════════════════════

def expA_torneo(w4, w6, n=80):
    log(f"\n=== A: torneo de 7 agentes ({n} batallas por par) ===")
    random.seed(101)
    agents = [
        ("Random",     lambda: RandomAgent()),
        ("H.Basica",   lambda: HeuristicBasicAgent()),
        ("H.Avanzada", lambda: HeuristicAdvancedAgent()),
        ("H.Mejorada", lambda: HeuristicImprovedAgent()),
        ("Minimax-d2", lambda: MinimaxAgent(depth=2)),
        ("Genetico-4", lambda: GeneticAgent(weights=w4, metadata={"minimax_depth": 2})),
        ("Genetico-6", lambda: GeneticImprovedAgent(weights=w6, metadata={"minimax_depth": 2})),
    ]
    names  = [a[0] for a in agents]
    totals = {a: [0, 0] for a in names}
    all_turns = all_draws = all_games = 0
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            na, fa = agents[i]; nb, fb = agents[j]
            wa, wb, draws, turns = duel(fa, fb, n)
            totals[na][0] += wa; totals[na][1] += n
            totals[nb][0] += wb; totals[nb][1] += n
            all_turns += turns; all_draws += draws; all_games += n
            log(f"  {na:11} vs {nb:11}: {wa/n*100:5.1f}%  turnos~{turns/n:4.1f}")
    overall = {a: round(totals[a][0] / totals[a][1] * 100, 1) for a in names}
    ci      = {a: wilson(totals[a][0], totals[a][1]) for a in names}
    log(f"  Global: {overall}")
    ALL["A_torneo"] = {"names": names, "overall": overall, "ci": ci, "n": n,
                       "avg_turns": round(all_turns / all_games, 1),
                       "draw_rate": round(all_draws / all_games * 100, 1)}
    save_json("A_torneo.json", ALL["A_torneo"])

    order  = sorted(names, key=lambda a: overall[a])
    vals   = [overall[a] for a in order]
    lo     = [overall[a] - ci[a][0] for a in order]
    hi     = [ci[a][1] - overall[a] for a in order]
    colors = ["#c0504d" if a == "Genetico-6" else
              "#e8a33d" if a == "Genetico-4" else "#4f81bd" for a in order]
    plt.figure(figsize=(6, 3.6))
    plt.barh(order, vals, xerr=[lo, hi], color=colors, capsize=3)
    plt.axvline(50, color="gray", ls="--", lw=0.8)
    plt.xlabel("Win-rate global (%) — IC 95% Wilson")
    plt.grid(alpha=0.3, axis="x")
    savefig("figA_torneo")


# ══ B. Poda alfa-beta: coste de búsqueda ═════════════════════════════════════════

def expB_poda(n_pos=40):
    log(f"\n=== B: poda alfa-beta (coste sobre {n_pos} posiciones) ===")
    random.seed(202)
    positions = [random_state() for _ in range(n_pos)]
    cost = {}
    for d in (1, 2, 3):
        np_ = full_ = 0; ms4 = ms6 = 0.0
        for st in positions:
            ag = MinimaxAgent(depth=d); ag.prune = True
            ag.choose_action(st.copy(), 1)
            s = ag.last_brain_data["stats"]; np_ += s["nodos"]; ms4 += s["ms"]
            ag2 = MinimaxAgent(depth=d); ag2.prune = False
            ag2.choose_action(st.copy(), 1)
            full_ += ag2.last_brain_data["stats"]["nodos"]
            ag3 = MinimaxImprovedAgent(depth=d)
            ag3.choose_action(st.copy(), 1)
            ms6 += ag3.last_brain_data["stats"]["ms"]
        cost[d] = {"nodos_poda": round(np_ / n_pos, 1),
                   "nodos_full": round(full_ / n_pos, 1),
                   "reduccion":  round((1 - np_ / full_) * 100, 1) if full_ else 0,
                   "ms_eval4":   round(ms4 / n_pos, 2),
                   "ms_eval6":   round(ms6 / n_pos, 2)}
        log(f"  d={d}: poda={cost[d]['nodos_poda']} full={cost[d]['nodos_full']} "
            f"reduc={cost[d]['reduccion']}%  ms4={cost[d]['ms_eval4']} ms6={cost[d]['ms_eval6']}")
    ALL["B_poda"] = {"cost": cost, "n_pos": n_pos}
    save_json("B_poda.json", ALL["B_poda"])

    ds = [1, 2, 3]
    plt.figure(figsize=(5, 3.3))
    plt.plot(ds, [cost[d]["nodos_full"] for d in ds], "o-", label="sin poda", color="#c0504d")
    plt.plot(ds, [cost[d]["nodos_poda"] for d in ds], "s-", label="con poda α-β", color="#4f81bd")
    plt.yscale("log")
    plt.xlabel("Profundidad"); plt.ylabel("Nodos por decisión (log)")
    plt.xticks(ds); plt.legend(); plt.grid(alpha=0.3)
    savefig("figB_poda")


# ══ C. Profundidad y calidad de juego ════════════════════════════════════════════

def expC_profundidad(n=80):
    log(f"\n=== C: profundidad y calidad ({n} batallas por profundidad) ===")
    wr = {}
    for d in (1, 2, 3):
        random.seed(300 + d)
        wa, wb, draws, turns = duel(lambda d=d: MinimaxAgent(depth=d),
                                    lambda: HeuristicBasicAgent(), n)
        wr[d] = {"winrate": round(wa / n * 100, 1), "ci": wilson(wa, n),
                 "turns": round(turns / n, 1)}
        log(f"  Minimax d={d} vs Basica: {wr[d]['winrate']}% CI{wr[d]['ci']} "
            f"turnos~{wr[d]['turns']}")
    ALL["C_profundidad"] = {"winrate_vs_basic": wr, "n": n}
    save_json("C_profundidad.json", ALL["C_profundidad"])

    ds  = [1, 2, 3]
    val = [wr[d]["winrate"] for d in ds]
    lo  = [wr[d]["winrate"] - wr[d]["ci"][0] for d in ds]
    hi  = [wr[d]["ci"][1] - wr[d]["winrate"] for d in ds]
    plt.figure(figsize=(5, 3.3))
    plt.errorbar(ds, val, yerr=[lo, hi], fmt="o-", color="#4f81bd", capsize=4,
                 label="win-rate vs H. Básica")
    plt.axhline(50, color="gray", ls="--", lw=0.8)
    plt.xlabel("Profundidad de búsqueda"); plt.ylabel("Win-rate (%)")
    plt.xticks(ds); plt.ylim(0, 100); plt.legend(); plt.grid(alpha=0.3)
    savefig("figC_profundidad")


# ══ D. Sobreajuste del genético: un rival vs panel ═══════════════════════════════
# Promediamos VARIAS semillas: el efecto de generalización es ruidoso con una sola
# corrida, así que medir la media ± desviación entre semillas evita depender de la
# suerte de un seed. El rival clave es Minimax-d2, NO visto por ninguna de las dos
# configuraciones de entrenamiento (single entrena vs Básica; panel vs R+B+A).

# Rivales de evaluación y su semilla de escenarios fija (CRN: todos los genéticos
# entrenados se prueban contra exactamente las mismas batallas).
_EVAL_RIVALS = [("Random",     lambda: RandomAgent(),            51),
                ("Basica",     lambda: HeuristicBasicAgent(),    52),
                ("Avanzada",   lambda: HeuristicAdvancedAgent(), 53),
                ("Minimax-d2", lambda: MinimaxAgent(depth=2),    54)]


def expD_panel(n=60, pop=10, gens=10, bpe=15, seeds=(7, 11, 17, 23, 31)):
    log(f"\n=== D: sobreajuste del genético, 1 rival vs panel "
        f"({len(seeds)} semillas, {n} bat/rival) ===")
    res = {"single": {r[0]: [] for r in _EVAL_RIVALS},
           "panel":  {r[0]: [] for r in _EVAL_RIVALS}}
    for sd in seeds:
        random.seed(sd)
        g_single = run_genetic(pop_size=pop, generations=gens, battles_per_eval=bpe,
                               minimax_depth=2, train_depth=1,
                               opponent_factories=[HeuristicBasicAgent])
        random.seed(sd)
        g_panel = run_genetic(pop_size=pop, generations=gens, battles_per_eval=bpe,
                              minimax_depth=2, train_depth=1, opponent_factories=PANEL)
        for cond, g in (("single", g_single), ("panel", g_panel)):
            for nm, fb, eseed in _EVAL_RIVALS:
                wr = duel_fixed(
                    lambda g=g: GeneticAgent(weights=g["weights"],
                                             metadata={"minimax_depth": 2}),
                    fb, n, eseed)
                res[cond][nm].append(wr)
        log(f"  semilla {sd}: single vs Mmx={res['single']['Minimax-d2'][-1]}% "
            f"panel vs Mmx={res['panel']['Minimax-d2'][-1]}%")

    def summarize(cond):
        out = {}; allv = []
        for nm, *_ in _EVAL_RIVALS:
            v = res[cond][nm]; allv += v
            out[nm] = {"mean": round(statistics.mean(v), 1),
                       "std":  round(statistics.pstdev(v), 1)}
        out["GLOBAL"] = {"mean": round(statistics.mean(allv), 1),
                         "std":  round(statistics.pstdev(allv), 1)}
        return out

    single, panel = summarize("single"), summarize("panel")
    log(f"  SINGLE: {single}")
    log(f"  PANEL : {panel}")
    ALL["D_panel"] = {"seeds": list(seeds), "n": n,
                      "train": {"pop": pop, "gens": gens, "bpe": bpe, "train_depth": 1},
                      "single": single, "panel": panel, "raw": res}
    save_json("D_panel.json", ALL["D_panel"])

    names = [r[0] for r in _EVAL_RIVALS]
    x = range(len(names)); width = 0.38
    plt.figure(figsize=(6, 3.4))
    plt.bar([i - width / 2 for i in x], [single[r]["mean"] for r in names], width,
            yerr=[single[r]["std"] for r in names], capsize=3,
            label="fitness vs 1 rival (Básica)", color="#c0504d")
    plt.bar([i + width / 2 for i in x], [panel[r]["mean"] for r in names], width,
            yerr=[panel[r]["std"] for r in names], capsize=3,
            label="fitness vs panel", color="#4f81bd")
    plt.xticks(list(x), names, fontsize=8)
    plt.axhline(50, color="gray", ls="--", lw=0.8)
    plt.ylabel("Win-rate medio (%)")
    plt.legend(fontsize=8); plt.grid(alpha=0.3, axis="y")
    savefig("figD_panel")


# ══ E. Techo de la evaluación: cuatro vs seis componentes ════════════════════════

def expE_techo(w4, w6, n_test=150):
    log(f"\n=== E: techo de la evaluación, 4 vs 6 pesos ({n_test} escenarios) ===")
    configs = [
        ("default-4",  [0.40, 0.35, 0.15, 0.10],             MinimaxAgent),
        ("genetico-4", w4,                                    MinimaxAgent),
        ("soloHP-4",   [0.0, 1.0, 0.0, 0.0],                 MinimaxAgent),
        ("default-6",  [0.25, 0.20, 0.20, 0.15, 0.10, 0.10], MinimaxImprovedAgent),
        ("genetico-6", w6,                                    MinimaxImprovedAgent),
        ("soloHP-6",   [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],       MinimaxImprovedAgent),
    ]
    techo = {}
    for name, w, cls in configs:
        techo[name] = {"weights": [round(x, 3) for x in w],
                       "d1": wr_vs_panel(w, 1, n_test, agent_class=cls),
                       "d2": wr_vs_panel(w, 2, n_test, agent_class=cls)}
        log(f"  {name:12} d1={techo[name]['d1']}%  d2={techo[name]['d2']}%")

    # Avanzada (4) vs Mejorada (6) a un nivel, con coste por decisión.
    Avz, Mej = HeuristicAdvancedAgent, HeuristicImprovedAgent
    Bas, Rnd = HeuristicBasicAgent, RandomAgent
    avz_mej = {
        "avanzada": {"vs_basica": duel_fixed(Avz, Bas, n_test, 42),
                     "vs_random": duel_fixed(Avz, Rnd, n_test, 43),
                     "ms_dec": bench_ms(Avz)},
        "mejorada": {"vs_basica": duel_fixed(Mej, Bas, n_test, 42),
                     "vs_random": duel_fixed(Mej, Rnd, n_test, 43),
                     "ms_dec": bench_ms(Mej)},
        "mejorada_vs_avanzada_h2h": duel_fixed(Mej, Avz, n_test, 44),
    }
    log(f"  Avanzada(4): {avz_mej['avanzada']}")
    log(f"  Mejorada(6): {avz_mej['mejorada']}")
    log(f"  Mejorada vs Avanzada (h2h): {avz_mej['mejorada_vs_avanzada_h2h']}%")
    ALL["E_techo"] = {"n_test": n_test, "techo": techo, "avz_vs_mej": avz_mej}
    save_json("E_techo.json", ALL["E_techo"])

    names = [c[0] for c in configs]
    d1v = [techo[nm]["d1"] for nm in names]
    d2v = [techo[nm]["d2"] for nm in names]
    x = range(len(names)); width = 0.38
    plt.figure(figsize=(7, 3.6))
    plt.bar([i - width / 2 for i in x], d1v, width, label="d=1", color="#4f81bd")
    plt.bar([i + width / 2 for i in x], d2v, width, label="d=2", color="#c0504d")
    plt.axhline(64, color="gray", ls="--", lw=1, label="techo (~64%)")
    plt.xticks(list(x), names, fontsize=8, rotation=15)
    plt.ylabel("Win-rate vs panel (%)")
    plt.legend(fontsize=8); plt.grid(alpha=0.3, axis="y")
    savefig("figE_techo")


# ══ Main ═════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    t0 = time.time()
    w4, w6 = train_genetics()
    expA_torneo(w4, w6, n=80)
    expB_poda(n_pos=40)
    expC_profundidad(n=80)
    expD_panel(n=60)
    expE_techo(w4, w6, n_test=150)
    save_json("results.json", ALL)
    log(f"\nTOTAL: {(time.time()-t0)/60:.1f} min. Resultados en results/ y figuras en figs/.")
