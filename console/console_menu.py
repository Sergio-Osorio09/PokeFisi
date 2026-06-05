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
║  4. Entrenar Heuristica Mejorada         ║
║  5. Entrenar IA Genetica                 ║
║  6. Eliminar pesos entrenados            ║
║  7. Salir                                ║
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
            _improved_train_flow()

        elif choice == "5":
            _genetic_flow()

        elif choice == "6":
            delete_trained_flow()

        elif choice == "7":
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


# ── Entrenamiento Heurística Mejorada ────────────────────────────────────────

def _improved_train_flow():
    from ai.trainer import run_training, save_weights
    from ai.heuristic_improved import HeuristicImprovedAgent, DEFAULT_WEIGHTS as IMP_WEIGHTS

    print("\n=== Entrenar Heuristica Mejorada ===")
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
    data = run_training(n, agent_class=HeuristicImprovedAgent, default_weights=IMP_WEIGHTS[:])
    path = save_weights(data, prefix="weights_improved")

    wr = data.get("win_rate", 0)
    print(f"\n  Entrenamiento completado!")
    print(f"  Guardado en:  {path}")
    print(f"  Win-rate:     {wr:.1%}")

    labels   = ["superv.", "hp_pond.", "ko_threat", "ko_danger", "cobertura", "velocidad"]
    weights  = data.get("weights", [])
    defaults = IMP_WEIGHTS

    if len(weights) == len(labels):
        print("\n  Pesos aprendidos:")
        for lbl, w, d in zip(labels, weights, defaults):
            diff = w - d
            sign = "+" if diff >= 0 else ""
            print(f"    {lbl:<12}  {w:.4f}  (base {d:.3f},  {sign}{diff:.4f})")
    else:
        print(f"\n  Pesos: {weights}")
    print()


# ── Entrenamiento genético ────────────────────────────────────────────────────

def _genetic_flow():
    from ai.genetic_trainer import run_genetic, save_genetic_weights
    from ai.heuristic_advanced import DEFAULT_WEIGHTS

    print("\n=== Entrenar IA Genetica ===")
    print("  Parametros configurables (Enter = valor por defecto):\n")

    def ask_int(prompt, default, min_val):
        while True:
            raw = input(f"  {prompt} [{default}]: ").strip()
            if raw == "":
                return default
            try:
                v = int(raw)
                if v >= min_val:
                    return v
                print(f"  [!] Minimo {min_val}.")
            except ValueError:
                print("  [!] Ingresa un numero entero.")

    print("  El AG evoluciona los pesos de un Minimax (poda alfa-beta).")
    print("  Minimax es costoso: valores altos pueden tardar varios minutos.\n")

    pop_size  = ask_int("Tamaño de poblacion (min. 4)",      12, 4)
    gens      = ask_int("Numero de generaciones (min. 5)",   15, 5)
    battles   = ask_int("Batallas por evaluacion (min. 10)", 20, 10)
    depth     = ask_int("Profundidad del Minimax (2 o 3)",    2, 2)

    labels = ["supervivencia", "hp_diff", "tipo", "velocidad"]
    total_evals = pop_size * gens

    print(f"\n  Configuracion:")
    print(f"    Poblacion         : {pop_size} individuos")
    print(f"    Generaciones      : {gens}")
    print(f"    Batallas/individuo: {battles}")
    print(f"    Profundidad Minimax: {depth} turno(s)")
    print(f"    Total evaluaciones: {total_evals * battles} batallas aprox.")
    print(f"\n  Iniciando evolucion...\n")

    def _callback(gen, total, best_gen, best_global, avg, population):
        bar_gen = "█" * int(best_gen * 10) + "░" * (10 - int(best_gen * 10))
        bar_glb = "█" * int(best_global * 10) + "░" * (10 - int(best_global * 10))
        print(f"  Gen {gen:>3}/{total}  |  "
              f"Mejor gen: {bar_gen} {best_gen:.0%}  |  "
              f"Mejor global: {bar_glb} {best_global:.0%}  |  "
              f"Promedio: {avg:.0%}")

    data = run_genetic(
        pop_size=pop_size,
        generations=gens,
        battles_per_eval=battles,
        minimax_depth=depth,
        callback=_callback,
    )

    path = save_genetic_weights(data)
    w    = data["weights"]

    print(f"\n  Evolucion completada!")
    print(f"  Guardado en: {path}")
    print(f"  Fitness final: {data['fitness']:.1%}")
    print(f"\n  Pesos evolucionados vs base:")
    for lbl, wv, dv in zip(labels, w, DEFAULT_WEIGHTS):
        diff = wv - dv
        sign = "+" if diff >= 0 else ""
        print(f"    {lbl:<14}  {wv:.4f}  (base {dv:.3f},  {sign}{diff:.4f})")
    print()


# ── Utilidades ────────────────────────────────────────────────────────────────

def _random_team(size: int) -> list[int]:
    return random.sample(range(1, 31), size)
