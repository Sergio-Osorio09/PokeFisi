from engine.state import BattleState
from engine.battle import Battle


def _hp_bar(current: int, max_hp: int, length: int = 20) -> str:
    filled = int((current / max_hp) * length)
    return "█" * filled + "░" * (length - filled)


def _team_icons(team: list) -> str:
    return "  ".join("✅" if p.is_alive() else "❌" for p in team)


def print_battle_state(state: BattleState):
    p1 = state.active_pokemon_p1
    p2 = state.active_pokemon_p2
    print("\n" + "=" * 52)
    print(f"  [IA] {p2.name:<14} HP: {_hp_bar(p2.current_hp, p2.max_hp)} {p2.current_hp:>4}/{p2.max_hp}")
    print(f"       Equipo: {_team_icons(state.player2_team)}")
    print()
    print(f"  [TU] {p1.name:<14} HP: {_hp_bar(p1.current_hp, p1.max_hp)} {p1.current_hp:>4}/{p1.max_hp}")
    print(f"       Equipo: {_team_icons(state.player1_team)}")
    print("=" * 52)


def human_choose_action(state: BattleState) -> dict:
    active = state.active_pokemon_p1
    moves = active.get_available_moves()
    print("\n--- ACCIONES ---")
    for i, m in enumerate(moves):
        print(f"  {i+1}. {m.name:<20} ({m.type}, Base {m.base_power})")
    # Opciones de cambio
    switch_options = [
        (i, p) for i, p in enumerate(state.player1_team)
        if p.is_alive() and i != state.active_index_p1
    ]
    switch_start = len(moves) + 1
    for j, (i, p) in enumerate(switch_options):
        print(f"  {switch_start + j}. Cambiar a {p.name}")

    total = len(moves) + len(switch_options)
    while True:
        raw = input(f"Elige acción (1-{total}): ").strip()
        try:
            choice = int(raw) - 1
            if 0 <= choice < len(moves):
                return {"type": "move", "move_index": choice}
            sw_idx = choice - len(moves)
            if 0 <= sw_idx < len(switch_options):
                poke_index, _ = switch_options[sw_idx]
                return {"type": "switch", "pokemon_index": poke_index}
            print("  [!] Opción inválida.")
        except ValueError:
            print("  [!] Ingresa un número.")


def run_console_battle_human_vs_ai(state: BattleState, human_agent, ai_agent):
    """Batalla interactiva donde el humano controla P1 y la IA controla P2."""
    from engine.battle import Battle

    battle = Battle(state, None, ai_agent)  # agent1=None, lo controlamos aquí

    print("\n¡Que empiece la batalla!\n")
    while not state.is_terminal():
        print_battle_state(state)
        state.turn_number += 1
        print(f"\n>>> Turno {state.turn_number} <<<")

        action1 = human_choose_action(state)
        action2 = ai_agent.choose_action(state, 2)

        # Resolver turno manualmente
        p1 = state.active_pokemon_p1
        p2 = state.active_pokemon_p2

        turn_log = []
        if p1.speed >= p2.speed:
            turn_log += _apply_and_log(state, 1, action1)
            if not state.is_terminal():
                turn_log += _apply_and_log(state, 2, action2)
        else:
            turn_log += _apply_and_log(state, 2, action2)
            if not state.is_terminal():
                turn_log += _apply_and_log(state, 1, action1)

        _auto_replace_console(state, turn_log)

        print("\n" + "-" * 40)
        for line in turn_log:
            print(line)
        print("-" * 40)
        input("[Presiona ENTER para continuar]")

    winner = state.get_winner()
    print(f"\n{'='*52}")
    if winner == 1:
        print("  ¡GANASTE! Felicidades.")
    else:
        print("  La IA ganó. ¡Mejor suerte la próxima!")
    print(f"{'='*52}\n")


def run_console_battle_ai_vs_ai(state: BattleState, agent1, agent2):
    from engine.battle import Battle
    battle = Battle(state, agent1, agent2)
    print(f"\nBatalla: {agent1.name}  vs  {agent2.name}\n")
    winner = battle.run()
    for line in battle.get_log():
        print(line)
    print(f"\nGanador: Jugador {winner}\n")
    return winner


# Helpers internos
from engine.damage import calculate_damage


def _apply_and_log(state: BattleState, player_id: int, action: dict) -> list[str]:
    log = []
    if action["type"] == "switch":
        idx = action["pokemon_index"]
        team = state.get_team(player_id)
        if team[idx].is_alive():
            state.set_active_index(player_id, idx)
            log.append(f"  P{player_id} cambió a {team[idx].name}!")
        return log

    move_index = action["move_index"]
    attacker = state.get_active(player_id)
    defender = state.get_active(3 - player_id)
    moves = attacker.get_available_moves()
    if move_index >= len(moves):
        move_index = 0
    move = moves[move_index]
    dmg, mult = calculate_damage(attacker, move, defender)

    if dmg == 0 and mult == 1.0:
        log.append(f"  {attacker.name} usó {move.name}... ¡Falló!")
    else:
        eff = ""
        if mult >= 2.0:
            eff = " ¡Muy efectivo!"
        elif mult == 0.0:
            eff = " No afecta..."
        elif mult < 1.0:
            eff = " Poco efectivo."
        defender.take_damage(dmg)
        log.append(
            f"  {'TÚ' if player_id==1 else 'IA'}: {attacker.name} usó {move.name}!"
            f" ({move.type}→{'/'.join(defender.types)}, x{mult:.1f}){eff}"
            f" → {dmg} daño. {defender.name} tiene {defender.current_hp}/{defender.max_hp} HP."
        )
        if not defender.is_alive():
            log.append(f"  ¡{defender.name} fue derrotado!")
    return log


def _auto_replace_console(state: BattleState, log: list[str]):
    for pid in (1, 2):
        active = state.get_active(pid)
        if not active.is_alive():
            idx = state.next_alive_index(pid)
            if idx >= 0:
                state.set_active_index(pid, idx)
                new_p = state.get_active(pid)
                log.append(f"  P{pid} envía a {new_p.name}!")
