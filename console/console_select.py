import json
from engine.loader import load_all_pokemon, load_moves, build_team
from ai.heuristic_trained import find_trained_weights, HeuristicTrainedAgent
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent
from ai.heuristic_advanced import HeuristicAdvancedAgent


def show_pokemon_table(pokemon_list: list[dict]):
    print("\n" + "=" * 60)
    print(f"  {'#':<4} {'Nombre':<14} {'Tipo':<16} {'HP':>4} {'ATK':>4} {'DEF':>4} {'SPE':>4}")
    print("-" * 60)
    for p in pokemon_list:
        types = "/".join(p["types"])
        s = p["stats"]
        print(
            f"  {p['id']:<4} {p['name']:<14} {types:<16} "
            f"{s['hp']:>4} {s['attack']:>4} {s['defense']:>4} {s['speed']:>4}"
        )
    print("=" * 60)


def select_team(label: str, team_size: int) -> list[int]:
    all_poke = load_all_pokemon()
    show_pokemon_table(all_poke)
    valid_ids = {p["id"] for p in all_poke}
    while True:
        raw = input(f"\n{label} — Elige {team_size} Pokemon (IDs separados por espacios): ").strip()
        try:
            chosen = list(dict.fromkeys(int(x) for x in raw.split()))
            chosen = [x for x in chosen if x in valid_ids]
            if len(chosen) < team_size:
                print(f"  [!] Necesitas elegir exactamente {team_size} Pokemon validos.")
                continue
            return chosen[:team_size]
        except ValueError:
            print("  [!] Ingresa solo numeros separados por espacios.")


def _build_ai_options() -> list[tuple[str, object]]:
    """Construye lista de (nombre, factory) incluyendo agentes entrenados disponibles."""
    options = [
        ("Agente Aleatorio",    lambda: RandomAgent()),
        ("Heuristica Basica",   lambda: HeuristicBasicAgent()),
        ("Heuristica Avanzada", lambda: HeuristicAdvancedAgent()),
    ]
    for path in find_trained_weights():
        p = path
        with open(p) as f:
            n = json.load(f)["battles"]
        options.append((f"HeuristicaAvanzada-{n}", lambda p=p: HeuristicTrainedAgent(p)))
    return options


def select_ai(label: str):
    options = _build_ai_options()
    print(f"\n{label}:")
    for i, (name, factory) in enumerate(options, 1):
        print(f"  {i}. {name}")
        for line in factory().get_info_lines():
            print(f"     {line}")
    print()
    while True:
        choice = input("  Elige IA: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                _, factory = options[idx]
                return factory()
        except ValueError:
            pass
        print("  [!] Opcion invalida.")


def select_team_size() -> int:
    while True:
        raw = input("\nTamano de equipo (3 o 4): ").strip()
        if raw in ("3", "4"):
            return int(raw)
        print("  [!] Escribe 3 o 4.")
