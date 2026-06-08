"""
Experimento E (informe): refinamiento del genético y techo de la evaluación.
  E1) Robustez del genético: 5 corridas con vs sin inmigrantes (piso del win-rate).
  E2) Techo de la evaluación de 4 pesos: default vs evolucionado vs "solo HP",
      win-rate frente al panel a profundidad 1 y 2.
  E3) ¿Importa la riqueza del eval? Avanzada (4) vs Mejorada (6): win-rate vs
      Básica/Aleatorio, enfrentamiento directo y ms por decisión.

Resultados -> docs/informe/results_E.json
Ejecutar desde la raíz del repo:  python docs/informe/run_experiment_E.py
Nota: entrena varios genéticos, así que tarda algunos minutos. Las cifras son
representativas (hay azar); coinciden en magnitud con las tablas del informe.
"""
import os, sys, json, time, random, statistics

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from engine.loader import load_moves, load_all_pokemon, build_team
from engine.state import BattleState
from engine.battle import Battle
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent
from ai.heuristic_improved import HeuristicImprovedAgent
from ai.minimax_agent import MinimaxAgent
from ai.genetic_trainer import run_genetic

MOVES = load_moves()
IDS   = [p["id"] for p in load_all_pokemon()]
PANEL = [RandomAgent, HeuristicBasicAgent, HeuristicAdvancedAgent]
OUT   = {}


def wr_vs_panel(weights, depth, n, seed0=777):
    """Win-rate (%) de Minimax(depth, weights) contra el panel, en n escenarios
    FIJOS (mismos para cualquier vector de pesos -> comparación justa, CRN)."""
    random.seed(seed0)
    scen = [(random.sample(IDS, 3), random.sample(IDS, 3),
             random.randrange(2**31), i % len(PANEL)) for i in range(n)]
    wins = 0
    for ids1, ids2, seed, oi in scen:
        random.seed(seed)
        opp = PANEL[oi]()
        st  = BattleState(build_team(ids1, MOVES), build_team(ids2, MOVES))
        if Battle(st, MinimaxAgent(depth=depth, weights=weights), opp).run() == 1:
            wins += 1
    return round(wins / n * 100, 1)


def duel_fixed(make_a, make_b, n, seed0):
    """Win-rate (%) de A (jugador 1) vs B en n escenarios fijos."""
    random.seed(seed0)
    scen = [(random.sample(IDS, 3), random.sample(IDS, 3)) for _ in range(n)]
    wa = 0
    for ids1, ids2 in scen:
        st = BattleState(build_team(ids1, MOVES), build_team(ids2, MOVES))
        if Battle(st, make_a(), make_b()).run() == 1:
            wa += 1
    return round(wa / n * 100, 1)


def bench_ms(make_agent, k=200):
    """Tiempo medio por decisión (ms) sobre k estados aleatorios."""
    ag = make_agent(); t = 0.0
    for _ in range(k):
        st = BattleState(build_team(random.sample(IDS, 3), MOVES),
                         build_team(random.sample(IDS, 3), MOVES))
        t0 = time.perf_counter(); ag.choose_action(st, 1); t += time.perf_counter() - t0
    return round(t / k * 1000, 1)


# ── E1: robustez del genético (inmigrantes) ────────────────────────────────────

def e1_robustez(runs=5, n_test=150):
    print(f"\n=== E1: robustez del genetico ({runs} corridas c/u) ===")

    def run_set(**kw):
        res = []
        for _ in range(runs):
            d = run_genetic(pop_size=14, generations=12, battles_per_eval=24,
                            minimax_depth=1, train_depth=1, opponent_factories=PANEL, **kw)
            res.append(wr_vs_panel(d["weights"], 1, n_test))
        return res

    random.seed(1)
    sin = run_set(immigrants=0, mutation_rate=0.15, mutation_strength=0.10, truncation=1.0)
    con = run_set(immigrants=2, mutation_rate=0.20, mutation_strength=0.15, truncation=0.40)

    def summ(r):
        return {"runs": r, "min": min(r), "mean": round(statistics.mean(r), 1), "max": max(r)}
    OUT["E1_robustez"] = {"sin_inmigrantes": summ(sin), "con_inmigrantes": summ(con), "n_test": n_test}
    print("  sin inmigrantes:", summ(sin))
    print("  con inmigrantes:", summ(con))


# ── E2: techo de la evaluación de 4 pesos ──────────────────────────────────────

def e2_techo(n_test=150):
    print("\n=== E2: techo de la evaluacion de 4 pesos ===")
    default = [0.40, 0.35, 0.15, 0.10]
    solo_hp = [0.0, 1.0, 0.0, 0.0]
    random.seed(3)
    g = run_genetic(pop_size=16, generations=15, battles_per_eval=24, minimax_depth=2,
                    train_depth=1, opponent_factories=PANEL,
                    immigrants=2, truncation=0.40, mutation_rate=0.20, mutation_strength=0.15)
    evolved = g["weights"]
    table = {}
    for name, w in [("default", default), ("evolucionado", evolved), ("solo_HP", solo_hp)]:
        table[name] = {"weights": [round(x, 3) for x in w],
                       "d1": wr_vs_panel(w, 1, n_test), "d2": wr_vs_panel(w, 2, n_test)}
        print(f"  {name:12} {table[name]['weights']}  d1={table[name]['d1']}%  d2={table[name]['d2']}%")
    OUT["E2_techo"] = {"n_test": n_test, **table}


# ── E3: Avanzada (4) vs Mejorada (6) ───────────────────────────────────────────

def e3_avz_mej(n=150):
    print(f"\n=== E3: Avanzada (4) vs Mejorada (6) ({n} batallas) ===")
    Avz, Mej = HeuristicAdvancedAgent, HeuristicImprovedAgent
    Bas, Rnd = HeuristicBasicAgent, RandomAgent
    res = {
        "avanzada": {"vs_basica": duel_fixed(Avz, Bas, n, 42),
                     "vs_random": duel_fixed(Avz, Rnd, n, 43),
                     "ms_dec": bench_ms(Avz)},
        "mejorada": {"vs_basica": duel_fixed(Mej, Bas, n, 42),
                     "vs_random": duel_fixed(Mej, Rnd, n, 43),
                     "ms_dec": bench_ms(Mej)},
        "mejorada_vs_avanzada_h2h": duel_fixed(Mej, Avz, n, 44),
        "n": n,
    }
    print("  Avanzada:", res["avanzada"])
    print("  Mejorada:", res["mejorada"])
    print("  Mejorada vs Avanzada (directo):", res["mejorada_vs_avanzada_h2h"], "%")
    OUT["E3_avanzada_vs_mejorada"] = res


if __name__ == "__main__":
    t0 = time.time()
    e1_robustez(runs=5, n_test=150)
    e2_techo(n_test=150)
    e3_avz_mej(n=150)
    out_path = os.path.join(os.path.dirname(__file__), "results_E.json")
    json.dump(OUT, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nTOTAL: {time.time()-t0:.0f}s -> results_E.json")
