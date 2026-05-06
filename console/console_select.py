from engine.loader import load_all_pokemon, load_moves, build_team
from ai.random_agent import RandomAgent
from ai.heuristic_basic import HeuristicBasicAgent


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
        raw = input(f"\n{label} — Elige {team_size} Pokémon (IDs separados por espacios): ").strip()
        try:
            chosen = list(dict.fromkeys(int(x) for x in raw.split()))
            chosen = [x for x in chosen if x in valid_ids]
            if len(chosen) < team_size:
                print(f"  [!] Necesitas elegir exactamente {team_size} Pokémon válidos.")
                continue
            return chosen[:team_size]
        except ValueError:
            print("  [!] Ingresa solo números separados por espacios.")


def select_ai(label: str):
    print(f"\n{label}:")
    print("  1. Agente Aleatorio")
    print("  2. Heurística Básica")
    while True:
        choice = input("  Elige IA: ").strip()
        if choice == "1":
            return RandomAgent()
        if choice == "2":
            return HeuristicBasicAgent()
        print("  [!] Opción inválida.")


def select_team_size() -> int:
    while True:
        raw = input("\nTamaño de equipo (3 o 4): ").strip()
        if raw in ("3", "4"):
            return int(raw)
        print("  [!] Escribe 3 o 4.")
