import json
from engine.loader import load_all_pokemon
from engine.pokemon import battle_stats
from ai.registry import build_registry


def show_pokemon_table(pokemon_list: list[dict]):
    print("\n" + "=" * 62)
    print(f"  {'#':<4} {'Nombre':<14} {'Tipo':<18} {'HP':>4} {'ATK':>4} {'DEF':>4} {'SPE':>4}")
    print("-" * 62)
    for p in pokemon_list:
        types = "/".join(p["types"])
        s = battle_stats(p["stats"])
        print(
            f"  {p['id']:<4} {p['name']:<14} {types:<18} "
            f"{s['hp']:>4} {s['attack']:>4} {s['defense']:>4} {s['speed']:>4}"
        )
    print("=" * 62)


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
                print(f"  [!] Necesitas {team_size} Pokemon validos (sin repetir).")
                continue
            return chosen[:team_size]
        except ValueError:
            print("  [!] Ingresa solo numeros separados por espacios.")


def select_ai(label: str):
    """Muestra todos los agentes disponibles (leídos del registro central) y devuelve uno."""
    options = build_registry()
    print(f"\n--- {label} ---")
    for i, (name, factory) in enumerate(options, 1):
        print(f"  {i}. {name}")
        for line in factory().get_info_lines():
            print(f"       {line}")
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
        raw = input("\nTamano de equipo (2-6): ").strip()
        try:
            n = int(raw)
            if 2 <= n <= 6:
                return n
        except ValueError:
            pass
        print("  [!] Escribe un numero entre 2 y 6.")


def delete_trained_flow():
    """Permite eliminar archivos de pesos entrenados."""
    from ai.heuristic_trained import find_trained_weights
    from ai.heuristic_improved import find_improved_weights
    import os

    paths = list(find_trained_weights()) + list(find_improved_weights())
    if not paths:
        print("\n  No hay pesos entrenados guardados.")
        return

    print("\n--- Pesos entrenados disponibles ---")
    for i, p in enumerate(paths, 1):
        name = os.path.basename(p)
        with open(p) as f:
            data = json.load(f)
        n = data.get("battles", "?")
        wr = data.get("win_rate", 0)
        print(f"  {i}. {name}  ({n} batallas, win-rate {wr:.1%})")

    raw = input("\nNumero a eliminar (0 = cancelar): ").strip()
    try:
        idx = int(raw) - 1
        if idx == -1:
            return
        if 0 <= idx < len(paths):
            os.remove(paths[idx])
            print(f"  Eliminado: {os.path.basename(paths[idx])}")
        else:
            print("  [!] Numero fuera de rango.")
    except ValueError:
        print("  [!] Ingresa un numero.")
