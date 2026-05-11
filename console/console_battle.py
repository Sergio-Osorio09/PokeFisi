import random
from engine.state import BattleState
from engine.battle import Battle


# ── Visualización del estado ──────────────────────────────────────────────────

def _hp_bar(current: int, max_hp: int, length: int = 20) -> str:
    filled = int((current / max_hp) * length) if max_hp > 0 else 0
    return "█" * filled + "░" * (length - filled)


def _team_strip(team: list, seen: set[int]) -> str:
    parts = []
    for i, p in enumerate(team):
        if i not in seen:
            parts.append("❓")          # no enviado aún
        elif p.is_alive():
            parts.append("✅")          # vivo
        else:
            parts.append("❌")          # derrotado
    return "  ".join(parts)


def print_battle_state(state: BattleState, seen_p1: set[int], seen_p2: set[int]):
    p1 = state.active_pokemon_p1
    p2 = state.active_pokemon_p2
    print("\n" + "=" * 58)
    print(f"  [IA] {p2.name:<14}  HP: {_hp_bar(p2.current_hp, p2.max_hp)}  {p2.current_hp:>4}/{p2.max_hp}")
    print(f"       Equipo: {_team_strip(state.player2_team, seen_p2)}")
    print()
    print(f"  [TU] {p1.name:<14}  HP: {_hp_bar(p1.current_hp, p1.max_hp)}  {p1.current_hp:>4}/{p1.max_hp}")
    print(f"       Equipo: {_team_strip(state.player1_team, seen_p1)}")
    print("=" * 58)


# ── Selección de acción humana ────────────────────────────────────────────────

def human_choose_action(state: BattleState) -> dict:
    active = state.active_pokemon_p1
    moves  = active.get_available_moves()
    print("\n--- ACCIONES ---")
    for i, m in enumerate(moves):
        print(f"  {i+1}. {m.name:<20}  ({m.type}, BP {m.base_power}, Acc {m.accuracy}%)")

    switch_options = [
        (i, p) for i, p in enumerate(state.player1_team)
        if p.is_alive() and i != state.active_index_p1
    ]
    if switch_options:
        print()
        for j, (i, p) in enumerate(switch_options):
            bar = _hp_bar(p.current_hp, p.max_hp, 12)
            print(f"  {len(moves)+j+1}. Cambiar a {p.name:<14}  {bar}  {p.current_hp}/{p.max_hp}")

    total = len(moves) + len(switch_options)
    while True:
        raw = input(f"\nElige accion (1-{total}): ").strip()
        try:
            choice = int(raw) - 1
            if 0 <= choice < len(moves):
                return {"type": "move", "move_index": choice}
            sw_idx = choice - len(moves)
            if 0 <= sw_idx < len(switch_options):
                poke_index, _ = switch_options[sw_idx]
                return {"type": "switch", "pokemon_index": poke_index}
            print("  [!] Opcion invalida.")
        except ValueError:
            print("  [!] Ingresa un numero.")


# ── Modo Humano vs IA ─────────────────────────────────────────────────────────

def run_console_battle_human_vs_ai(state: BattleState, ai_agent):
    """
    Usa el mismo engine que la GUI: Battle._apply_and_log_action + _auto_replace_log.
    Garantiza reglas idénticas en ambos modos.
    """
    battle   = Battle(state, None, ai_agent)
    seen_p1  = {state.active_index_p1}
    seen_p2  = {state.active_index_p2}

    print("\n¡Que empiece la batalla!\n")

    while not state.is_terminal():
        print_battle_state(state, seen_p1, seen_p2)
        state.turn_number += 1
        print(f"\n>>> Turno {state.turn_number} <<<")
        battle.log.append(f"=== Turno {state.turn_number} ===")

        action1 = human_choose_action(state)
        action2 = ai_agent.choose_action(state, 2)

        p1 = state.active_pokemon_p1
        p2 = state.active_pokemon_p2
        new_lines: list[str] = []

        p1_first = p1.speed > p2.speed or (p1.speed == p2.speed and random.random() < 0.5)
        if p1_first:
            new_lines += battle._apply_and_log_action(state, 1, action1)
            if not state.is_terminal():
                new_lines += battle._apply_and_log_action(state, 2, action2)
        else:
            new_lines += battle._apply_and_log_action(state, 2, action2)
            if not state.is_terminal():
                new_lines += battle._apply_and_log_action(state, 1, action1)

        battle._auto_replace_log(state, new_lines)

        # Actualizar rastreo de Pokémon vistos
        seen_p1.add(state.active_index_p1)
        seen_p2.add(state.active_index_p2)

        print("\n" + "-" * 42)
        for line in new_lines:
            print(line)
        print("-" * 42)
        input("[Presiona ENTER para continuar]")

    winner = state.get_winner()
    print(f"\n{'='*58}")
    if winner == 1:
        print("  ¡GANASTE! Felicidades.")
    elif winner == 2:
        print("  La IA gano. ¡Mejor suerte la proxima!")
    else:
        print("  ¡Empate!")
    print(f"{'='*58}\n")


# ── Modo IA vs IA ─────────────────────────────────────────────────────────────

def run_console_battle_ai_vs_ai(state: BattleState, agent1, agent2,
                                 verbose: bool = True) -> int:
    """
    Ejecuta la batalla completa usando el engine central.
    verbose=False útil para experimentos masivos.
    """
    battle = Battle(state, agent1, agent2)
    if verbose:
        print(f"\nBatalla: {agent1.name}  vs  {agent2.name}\n")

    winner = battle.run()

    if verbose:
        for line in battle.get_log():
            print(line)
        if winner:
            print(f"\nGanador: Jugador {winner} ({(agent1 if winner==1 else agent2).name})\n")
        else:
            print("\n¡Empate!\n")

    return winner
