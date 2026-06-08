"""
Experimentos y torneo de IAs (headless), con reportes documentados en results/.

Uso:
    python run_arena.py [n_batallas_por_par]   (por defecto 30)

Genera:
    results/round_robin_<fecha>.{json,md}   — clasificación + matriz head-to-head
    results/torneo_<fecha>.{json,md}        — bracket del torneo (si nº = potencia de 2)

Por defecto excluye las IAs de profundidad 3 (lentas); edita EXCLUDE_SUBSTR para incluirlas.
"""
import sys
import random

from arena import core, report
from ai import registry

EXCLUDE_SUBSTR = ("d=3",)   # nombres que contengan esto se omiten (lentos)


def _selected_competitors():
    sel = []
    for i, (name, _) in enumerate(registry.AI_REGISTRY):
        if any(s in name for s in EXCLUDE_SUBSTR):
            continue
        sel.append((i, 1))
    return core.registry_competitors(sel)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    random.seed(2026)
    comp = _selected_competitors()
    print(f"== Round-robin: {len(comp)} IAs x {n} batallas/par ==")
    rr = core.round_robin(
        comp, n_battles=n, size=3, bench_k=15,
        progress=lambda d, t, a, b: print(f"  [{d}/{t}] {a} vs {b}"))
    jp, mp = report.save_round_robin(rr, tag="round_robin")
    print("\n-- Clasificación --")
    for r in rr["leaderboard"]:
        print(f"  #{r['rank']} {r['name']:26} {r['winrate']:5.1f}%  ({r['decision_ms']} ms)")
    print("Reporte:", mp)

    # Torneo con los primeros 2^k competidores (potencia de 2 más grande que quepa).
    k = 1
    while (1 << (k + 1)) <= len(comp):
        k += 1
    pot = 1 << k
    if pot >= 2:
        print(f"\n== Torneo eliminatorio: {pot} competidores (mejor de 3) ==")
        br = core.run_bracket(comp[:pot], best_of=3, size=3,
                              on_match=lambda ri, mi, m: print(
                                  f"  R{ri+1} {m['a']} vs {m['b']} -> {m['winner']} {m['score']}"))
        jp2, mp2 = report.save_bracket(br, tag="torneo")
        print("Campeón:", br["champion"], "| Reporte:", mp2)


if __name__ == "__main__":
    main()
