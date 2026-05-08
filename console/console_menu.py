import random
from engine.loader import load_moves, build_team
from engine.state import BattleState
from console.console_select import select_team, select_ai, select_team_size, delete_trained_flow
from console.console_battle import run_console_battle_human_vs_ai, run_console_battle_ai_vs_ai


def _print_banner():
    print("""
╔══════════════════════════════════════════╗
║            POKEFISI  - Consola           ║
╠══════════════════════════════════════════╣
║  1. Humano vs IA                         ║
║  2. IA vs IA                             ║
║  3. Entrenar Heuristica Avanzada         ║
║  4. Eliminar pesos entrenados            ║
║  5. Salir                                ║
╚══════════════════════════════════════════╝""")


def start_console():
    all_moves = load_moves()
    while True:
        _print_banner()
        choice = input("Elige una opcion: ").strip()

        if choice == "1":
            _human_vs_ai_flow(all_moves)

        elif choice == "2":
            _ai_vs_ai_flow(all_moves)

        elif choice == "3":
            _train_flow()

        elif choice == "4":
            delete_trained_flow()

        elif choice == "5":
            print("\n¡Hasta luego!\n")
            break

        else:
            print("  [!] Opcion invalida.")


# ── Flujos de batalla ─────────────────────────────────────────────────────────

def _human_vs_ai_flow(all_moves):
    size     = select_team_size()
    ai_agent = select_ai("IA rival")

    human_ids = select_team("Tu equipo", size)
    ai_ids    = _random_team(size)
    print(f"\n  Equipo de la IA (aleatorio): IDs {ai_ids}")

    team1 = build_team(human_ids, all_moves)
    team2 = build_team(ai_ids,    all_moves)
    state = BattleState(team1, team2)
    run_console_battle_human_vs_ai(state, ai_agent)


def _ai_vs_ai_flow(all_moves):
    size    = select_team_size()
    agent1  = select_ai("IA Jugador 1")
    agent2  = select_ai("IA Jugador 2")

    print("\n¿Como configurar los equipos?")
    print("  1. Equipos aleatorios")
    print("  2. Seleccionar manualmente")
    cfg = input("  Elige: ").strip()

    if cfg == "2":
        ids1 = select_team(f"Equipo de {agent1.name}", size)
        ids2 = select_team(f"Equipo de {agent2.name}", size)
    else:
        ids1 = _random_team(size)
        ids2 = _random_team(size)
        print(f"\n  Equipo IA1: IDs {ids1}")
        print(f"  Equipo IA2: IDs {ids2}")

    team1 = build_team(ids1, all_moves)
    team2 = build_team(ids2, all_moves)
    state = BattleState(team1, team2)
    run_console_battle_ai_vs_ai(state, agent1, agent2, verbose=True)


# ── Entrenamiento ─────────────────────────────────────────────────────────────

def _train_flow():
    from ai.trainer import run_training, save_weights
    from ai.heuristic_advanced import DEFAULT_WEIGHTS

    print("\n=== Entrenar Heuristica Avanzada ===")
    while True:
        raw = input("  ¿Cuantas batallas para entrenar? (min. 10): ").strip()
        try:
            n = int(raw)
            if n >= 10:
                break
            print("  [!] Ingresa al menos 10 batallas.")
        except ValueError:
            print("  [!] Ingresa un numero entero.")

    print(f"  Entrenando con {n} batallas...")
    data = run_training(n)
    path = save_weights(data)

    wr = data.get("win_rate", 0)
    print(f"\n  Entrenamiento completado!")
    print(f"  Guardado en:  {path}")
    print(f"  Win-rate:     {wr:.1%}")

    # Los pesos tienen 4 componentes (reformulacion diferencial)
    labels = ["supervivencia", "hp_diff", "tipo", "velocidad"]
    weights  = data.get("weights", [])
    defaults = DEFAULT_WEIGHTS

    if len(weights) == len(labels):
        print("\n  Pesos aprendidos:")
        for lbl, w, d in zip(labels, weights, defaults):
            diff = w - d
            sign = "+" if diff >= 0 else ""
            print(f"    {lbl:<14}  {w:.4f}  (base {d:.3f},  {sign}{diff:.4f})")
    else:
        print(f"\n  Pesos: {weights}")
    print()


# ── Utilidades ────────────────────────────────────────────────────────────────

def _random_team(size: int) -> list[int]:
    return random.sample(range(1, 31), size)
