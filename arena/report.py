"""
Escritores de reportes documentados (JSON + Markdown) para experimentos y
torneos. Los resultados se guardan en results/ (legibles y versionables).
"""
import os
import json
import time

RESULTS_DIR = "results"


def _ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def _ensure_dir():
    os.makedirs(RESULTS_DIR, exist_ok=True)


def save_round_robin(rr: dict, tag: str = "experimento") -> tuple[str, str]:
    """Guarda un round-robin como JSON + Markdown. Devuelve (json_path, md_path)."""
    _ensure_dir()
    base = f"{tag}_{_ts()}"
    json_path = os.path.join(RESULTS_DIR, base + ".json")
    md_path = os.path.join(RESULTS_DIR, base + ".md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rr, f, ensure_ascii=False, indent=2)

    L = []
    L.append(f"# Experimento de IAs — {tag}")
    L.append("")
    L.append(f"- **Fecha:** {time.strftime('%Y-%m-%d %H:%M')}")
    L.append(f"- **Batallas por par:** {rr['n_battles']}  |  **Equipos:** "
             f"{rr['team_size']}v{rr['team_size']} (aleatorios independientes)")
    L.append(f"- **Pokémon excluidos:** {', '.join(rr['excluded_pokemon'])}  "
             f"(pool de {rr['pool_size']})")
    L.append(f"- **Tasa de empates:** {rr['draw_rate']}%")
    L.append("")
    L.append("## Clasificación (leaderboard)")
    L.append("")
    L.append("| # | IA | Win-rate | IC 95% (Wilson) | Turnos | Margen | ms/jugada |")
    L.append("|---|----|---------:|:---------------:|-------:|-------:|----------:|")
    for r in rr["leaderboard"]:
        ci = f"[{r['ci'][0]}, {r['ci'][1]}]"
        L.append(f"| {r['rank']} | {r['name']} | **{r['winrate']}%** | {ci} | "
                 f"{r['avg_turns']} | {r['avg_margin']} | {r['decision_ms']} |")
    L.append("")
    L.append("### Métricas")
    L.append("- **Win-rate**: % de batallas ganadas (todos contra todos).")
    L.append("- **IC 95%**: intervalo de confianza de Wilson.")
    L.append("- **Turnos**: duración media de las batallas.")
    L.append("- **Margen**: fuerza de equipo restante al ganar (0–1; más alto = más contundente).")
    L.append("- **ms/jugada**: tiempo medio de decisión (costo computacional).")
    L.append("")
    L.append("## Matriz head-to-head (% de victorias de FILA vs COLUMNA)")
    L.append("")
    names = rr["names"]
    L.append("| vs | " + " | ".join(names) + " |")
    L.append("|----|" + "|".join([":---:"] * len(names)) + "|")
    for a in names:
        cells = []
        for b in names:
            v = rr["matrix"][a][b]
            cells.append("—" if v is None else f"{v}")
        L.append(f"| **{a}** | " + " | ".join(cells) + " |")
    L.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return json_path, md_path


def save_bracket(br: dict, tag: str = "torneo") -> tuple[str, str]:
    """Guarda un torneo (bracket) como JSON + Markdown."""
    _ensure_dir()
    base = f"{tag}_{_ts()}"
    json_path = os.path.join(RESULTS_DIR, base + ".json")
    md_path = os.path.join(RESULTS_DIR, base + ".md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(br, f, ensure_ascii=False, indent=2)

    n = len(br["competitors"])
    L = []
    L.append(f"# Torneo de IAs — {tag}")
    L.append("")
    L.append(f"- **Fecha:** {time.strftime('%Y-%m-%d %H:%M')}")
    L.append(f"- **Competidores:** {n}  |  **Formato:** eliminatoria, mejor de "
             f"{br['best_of']}  |  **Equipos:** {br['team_size']}v{br['team_size']} "
             f"aleatorios")
    L.append(f"- **Pokémon excluidos:** {', '.join(br['excluded_pokemon'])}")
    L.append("")
    L.append(f"## 🏆 Campeón: **{br['champion']}**")
    L.append("")
    round_names = _round_names(len(br["rounds"]))
    for ri, rnd in enumerate(br["rounds"]):
        L.append(f"### {round_names[ri]}")
        L.append("")
        for m in rnd:
            L.append(f"- **{m['a']}** vs **{m['b']}** → 🏆 **{m['winner']}** "
                     f"(marcador {m['score'][0]}–{m['score'][1]})")
        L.append("")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return json_path, md_path


def _round_names(n_rounds: int) -> list[str]:
    """Nombres de ronda (cuartos, semis, final…) según cuántas haya."""
    base = ["Final", "Semifinales", "Cuartos de final", "Octavos de final",
            "Dieciseisavos"]
    names = []
    for i in range(n_rounds):
        # la última ronda es la Final; las anteriores van hacia atrás
        from_end = n_rounds - 1 - i
        names.append(base[from_end] if from_end < len(base) else f"Ronda {i + 1}")
    return names
