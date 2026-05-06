from engine.loader import load_moves, build_team
from engine.state import BattleState
from console.console_select import select_team, select_ai, select_team_size
from console.console_battle import run_console_battle_human_vs_ai, run_console_battle_ai_vs_ai
from ai.random_agent import RandomAgent


def _print_banner():
    print("""
╔══════════════════════════════════╗
║          POKEFISI  🎮            ║
╠══════════════════════════════════╣
║  1. Humano vs IA                 ║
║  2. IA vs IA                     ║
║  3. Salir                        ║
╚══════════════════════════════════╝""")


def start_console():
    all_moves = load_moves()
    while True:
        _print_banner()
        choice = input("Elige una opción: ").strip()

        if choice == "1":
            size = select_team_size()
            human_ids = select_team("Tu equipo", size)
            ai_agent = select_ai("IA Jugador 2")
            ai_ids = _random_team(size)
            print(f"\nEquipo de la IA: {ai_ids}")

            team1 = build_team(human_ids, all_moves)
            team2 = build_team(ai_ids, all_moves)
            state = BattleState(team1, team2)
            run_console_battle_human_vs_ai(state, None, ai_agent)

        elif choice == "2":
            size = select_team_size()
            agent1 = select_ai("IA Jugador 1")
            agent2 = select_ai("IA Jugador 2")
            ids1 = _random_team(size)
            ids2 = _random_team(size)
            print(f"\nEquipo IA1: {ids1}")
            print(f"Equipo IA2: {ids2}")

            team1 = build_team(ids1, all_moves)
            team2 = build_team(ids2, all_moves)
            state = BattleState(team1, team2)
            run_console_battle_ai_vs_ai(state, agent1, agent2)

        elif choice == "3":
            print("\n¡Hasta luego!\n")
            break
        else:
            print("  [!] Opción inválida.")


def _random_team(size: int) -> list[int]:
    import random
    return random.sample(range(1, 31), size)
