"""
Núcleo headless de experimentos y torneos de IAs.

Reutilizable por:
  - el script de experimentos (genera reportes documentados), y
  - el modo Torneo de la GUI (bracket animado).

Reglas (decididas con el usuario):
  - Equipos ALEATORIOS e INDEPENDIENTES por batalla (cada IA el suyo).
  - Se excluyen Pokémon desbalanceados del pool (ver EXCLUDED_POKEMON).
  - Las llaves del torneo se juegan al MEJOR DE 3.
"""
import math
import time
import random

from engine.loader import load_moves, load_all_pokemon, build_team
from engine.state import BattleState
from engine.battle import Battle

# Pokémon excluidos por desbalanceados (decisión del equipo).
EXCLUDED_POKEMON = {"Mewtwo", "Dragonite", "Cloyster", "Snorlax"}

_MOVES = load_moves()
_ALL_POKEMON = load_all_pokemon()
# Pool de Pokémon permitidos para los equipos aleatorios.
TEAM_POOL = [p["id"] for p in _ALL_POKEMON if p["name"] not in EXCLUDED_POKEMON]


# ── Utilidades ────────────────────────────────────────────────────────────────

def team_strength(team) -> float:
    """Fuerza restante de un equipo en [0,1]: Pokémon vivos + HP."""
    total = len(team)
    if total == 0:
        return 0.0
    alive = sum(1 for p in team if p.is_alive())
    hp = sum(p.hp_ratio() for p in team)
    return (alive + hp) / (2 * total)


def random_teams(size: int = 3):
    """Dos equipos aleatorios e independientes del pool permitido."""
    return (build_team(random.sample(TEAM_POOL, size), _MOVES),
            build_team(random.sample(TEAM_POOL, size), _MOVES))


def wilson(wins: int, n: int, z: float = 1.96):
    """Intervalo de confianza de Wilson (95%) para una proporción, en %."""
    if n == 0:
        return (0.0, 0.0)
    p = wins / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return (round((c - h) * 100, 1), round((c + h) * 100, 1))


# ── Batalla y match (mejor de N) ───────────────────────────────────────────────

def play_battle(agent1, agent2, size: int = 3):
    """Una batalla con equipos aleatorios independientes (agent1 = jugador 1).
    Devuelve (winner, turns, margin) — margin = fuerza restante del ganador."""
    t1, t2 = random_teams(size)
    state = BattleState(t1, t2)
    winner = Battle(state, agent1, agent2).run()
    turns = state.turn_number
    if winner == 1:
        margin = team_strength(state.player1_team)
    elif winner == 2:
        margin = team_strength(state.player2_team)
    else:
        margin = 0.0
    return winner, turns, margin


def play_match(facA, facB, best_of: int = 3, size: int = 3) -> dict:
    """Mejor de `best_of`. Equipos aleatorios por batalla; lados alternados para
    reducir el sesgo de quién juega primero. facA/facB = factories (callables).

    Devuelve {winner: 0(A)|1(B), score: [a, b], battles: [...]}."""
    need = best_of // 2 + 1
    a = b = 0
    battles = []
    i = 0
    cap = best_of * 3  # salvaguarda contra empates repetidos
    while a < need and b < need and i < cap:
        if i % 2 == 0:
            w, turns, margin = play_battle(facA(), facB(), size)
            a_won = (w == 1)
        else:
            w, turns, margin = play_battle(facB(), facA(), size)
            a_won = (w == 2)
        i += 1
        if w == 0 or w is None:        # empate (raro): no cuenta
            battles.append({"winner": None, "turns": turns})
            continue
        if a_won:
            a += 1
        else:
            b += 1
        battles.append({"winner": "A" if a_won else "B",
                        "turns": turns, "margin": round(margin, 3)})
    return {"winner": 0 if a >= b else 1, "score": [a, b], "battles": battles}


# ── Benchmark de tiempo de decisión ────────────────────────────────────────────

def benchmark_decision_ms(factory, k: int = 25, size: int = 3) -> float:
    """Tiempo medio (ms) que tarda la IA en elegir una acción, sobre k estados."""
    agent = factory()
    total = 0.0
    for _ in range(k):
        t1, t2 = random_teams(size)
        st = BattleState(t1, t2)
        s = time.perf_counter()
        agent.choose_action(st, 1)
        total += (time.perf_counter() - s) * 1000.0
    return round(total / k, 2) if k else 0.0


# ── Round-robin (todos contra todos) + leaderboard ─────────────────────────────

def round_robin(competitors, n_battles: int = 40, size: int = 3,
                bench_k: int = 20, progress=None) -> dict:
    """competitors: lista de (label, factory) con labels únicos.

    Cada par juega `n_battles` (lados alternados). Devuelve métricas por IA,
    matriz head-to-head y leaderboard ordenado por win-rate."""
    names = [c[0] for c in competitors]
    facs = dict(competitors)

    matrix = {a: {b: None for b in names} for a in names}
    wins = {a: 0 for a in names}
    games = {a: 0 for a in names}
    turns_sum = {a: 0 for a in names}
    margin_sum = {a: 0.0 for a in names}
    margin_cnt = {a: 0 for a in names}
    draws_total = 0
    pairs = [(i, j) for i in range(len(names)) for j in range(i + 1, len(names))]
    done = 0

    for i, j in pairs:
        na, nb = names[i], names[j]
        wa = wb = 0
        for k in range(n_battles):
            if k % 2 == 0:
                w, turns, margin = play_battle(facs[na](), facs[nb](), size)
                a_id, b_id = 1, 2
            else:
                w, turns, margin = play_battle(facs[nb](), facs[na](), size)
                a_id, b_id = 2, 1
            turns_sum[na] += turns
            turns_sum[nb] += turns
            if w == a_id:
                wa += 1; margin_sum[na] += margin; margin_cnt[na] += 1
            elif w == b_id:
                wb += 1; margin_sum[nb] += margin; margin_cnt[nb] += 1
            else:
                draws_total += 1
        matrix[na][nb] = round(wa / n_battles * 100, 1)
        matrix[nb][na] = round(wb / n_battles * 100, 1)
        wins[na] += wa; wins[nb] += wb
        games[na] += n_battles; games[nb] += n_battles
        done += 1
        if progress:
            progress(done, len(pairs), na, nb)

    decision_ms = {n: benchmark_decision_ms(facs[n], bench_k, size) for n in names}

    rows = []
    for n in names:
        g = games[n]
        wr = round(wins[n] / g * 100, 1) if g else 0.0
        rows.append({
            "name": n,
            "winrate": wr,
            "ci": wilson(wins[n], g),
            "wins": wins[n], "games": g,
            "avg_turns": round(turns_sum[n] / g, 1) if g else 0.0,
            "avg_margin": round(margin_sum[n] / margin_cnt[n], 3) if margin_cnt[n] else 0.0,
            "decision_ms": decision_ms[n],
        })
    rows.sort(key=lambda r: r["winrate"], reverse=True)
    for rank, r in enumerate(rows, 1):
        r["rank"] = rank

    return {
        "names": names,
        "n_battles": n_battles,
        "team_size": size,
        "matrix": matrix,
        "leaderboard": rows,
        "draw_rate": round(draws_total / (len(pairs) * n_battles) * 100, 1) if pairs else 0.0,
        "excluded_pokemon": sorted(EXCLUDED_POKEMON),
        "pool_size": len(TEAM_POOL),
    }


# ── Torneo eliminatorio (bracket, mejor de N) ──────────────────────────────────

def run_bracket(competitors, best_of: int = 3, size: int = 3, on_match=None) -> dict:
    """competitors: lista de (label, factory); la longitud debe ser potencia de 2
    (2, 4, 8...). Eliminatoria simple al mejor de `best_of`.

    on_match(round_idx, match_idx, match_dict): callback tras cada llave (para
    animar el bracket en la GUI).

    Devuelve {competitors, rounds, champion, ...}."""
    n = len(competitors)
    if n < 2 or (n & (n - 1)) != 0:
        raise ValueError("El nº de competidores debe ser potencia de 2 (2, 4, 8...).")

    current = list(competitors)      # [(label, factory), ...]
    rounds = []
    while len(current) > 1:
        ri = len(rounds)
        round_matches = []
        next_round = []
        for mi, k in enumerate(range(0, len(current), 2)):
            la, fa = current[k]
            lb, fb = current[k + 1]
            res = play_match(fa, fb, best_of, size)
            win = current[k] if res["winner"] == 0 else current[k + 1]
            match = {
                "a": la, "b": lb,
                "score": res["score"],
                "winner": win[0],
                "battles": res["battles"],
            }
            round_matches.append(match)
            next_round.append(win)
            if on_match:
                on_match(ri, mi, match)
        rounds.append(round_matches)
        current = next_round

    return {
        "competitors": [c[0] for c in competitors],
        "best_of": best_of,
        "team_size": size,
        "rounds": rounds,
        "champion": current[0][0],
        "excluded_pokemon": sorted(EXCLUDED_POKEMON),
    }


# ── Helpers de selección desde el registro ─────────────────────────────────────

def registry_competitors(selection) -> list:
    """selection: lista de (registry_index, cantidad). Devuelve [(label, factory)]
    con labels únicos (#1, #2 si se repite la misma IA)."""
    from ai import registry
    reg = registry.AI_REGISTRY
    out = []
    for idx, count in selection:
        base_name, factory = reg[idx]
        for c in range(count):
            label = base_name if count == 1 else f"{base_name} #{c + 1}"
            out.append((label, factory))
    return out
