import random
from engine.state import BattleState
from engine.damage import calculate_damage

# Tope de turnos: evita batallas infinitas (p.ej. Normal vs Ghost que no se
# pueden hacer daño, o agentes que solo cambian). Un 3v3 real acaba en <50.
MAX_TURNS = 200


class Battle:
    def __init__(self, state: BattleState, agent1, agent2):
        self.state = state
        self.agent1 = agent1
        self.agent2 = agent2
        self.log: list[str] = []
        self.finished = False

    def _log(self, msg: str):
        self.log.append(msg)

    def run(self):
        while not self.state.is_terminal() and self.state.turn_number < MAX_TURNS:
            self.step()

        winner = self.state.get_winner()
        if winner is None and self.state.is_terminal() is False:
            # Se alcanzó el tope de turnos: decidir por desempate.
            winner = self._winner_on_timeout()
            self._log(f"--- Tope de {MAX_TURNS} turnos alcanzado. Ganador: {winner} ---")
        else:
            self._log(f"--- Batalla terminada. Ganador: Jugador {winner} ---")

        self.finished = True
        if self.agent1:
            self.agent1.on_battle_end(winner == 1)
        if self.agent2:
            self.agent2.on_battle_end(winner == 2)
        return winner

    def _winner_on_timeout(self):
        """Desempate al agotar turnos: más Pokémon vivos; si empatan, más HP
        total; si aún empatan, sin ganador (None)."""
        def alive(pid):
            return sum(1 for p in self.state.get_team(pid) if p.is_alive())
        def hp_total(pid):
            return sum(p.hp_ratio() for p in self.state.get_team(pid))

        a1, a2 = alive(1), alive(2)
        if a1 != a2:
            return 1 if a1 > a2 else 2
        h1, h2 = hp_total(1), hp_total(2)
        if abs(h1 - h2) > 1e-9:
            return 1 if h1 > h2 else 2
        return None

    def step(self):
        """Ejecuta un turno completo y retorna las líneas de log generadas."""
        if self.state.is_terminal():
            return []

        prev_log_len = len(self.log)
        self.state.turn_number += 1
        self._log(f"=== Turno {self.state.turn_number} ===")

        action1 = self.agent1.choose_action(self.state, 1)
        action2 = self.agent2.choose_action(self.state, 2)

        # Orden por velocidad; empate se resuelve al azar (regla Pokémon)
        p1 = self.state.active_pokemon_p1
        p2 = self.state.active_pokemon_p2
        p1_first = p1.speed > p2.speed or (p1.speed == p2.speed and random.random() < 0.5)
        if p1_first:
            self._execute_action(1, action1)
            if not self.state.is_terminal():
                self._execute_action(2, action2)
        else:
            self._execute_action(2, action2)
            if not self.state.is_terminal():
                self._execute_action(1, action1)

        # Reemplazar caídos automáticamente
        self._auto_replace(1)
        self._auto_replace(2)

        return self.log[prev_log_len:]

    def _execute_action(self, player_id: int, action: dict):
        if action["type"] == "move":
            self._execute_move(player_id, action["move_index"])
        elif action["type"] == "switch":
            self._execute_switch(player_id, action["pokemon_index"])

    def _execute_move(self, player_id: int, move_index: int):
        attacker = self.state.get_active(player_id)
        defender = self.state.get_active(3 - player_id)

        if not attacker.is_alive():
            return

        moves = attacker.get_available_moves()
        if move_index >= len(moves):
            move_index = 0
        move = moves[move_index]

        damage, mult = calculate_damage(attacker, move, defender)

        if damage == 0 and mult == 1.0:
            self._log(f"  P{player_id} {attacker.name} usó {move.name}... ¡Falló!")
        else:
            eff = ""
            if mult >= 2.0:
                eff = " ¡Muy efectivo!"
            elif mult == 0.0:
                eff = " No afecta..."
            elif mult < 1.0:
                eff = " Poco efectivo."

            defender.take_damage(damage)
            self._log(
                f"  P{player_id} {attacker.name} usó {move.name}! "
                f"({move.type}→{'/'.join(defender.types)}, x{mult:.1f}){eff} "
                f"→ {damage} daño. {defender.name} tiene {defender.current_hp}/{defender.max_hp} HP."
            )

        if not defender.is_alive():
            self._log(f"  ¡{defender.name} fue derrotado!")

    def _execute_switch(self, player_id: int, pokemon_index: int):
        team = self.state.get_team(player_id)
        if pokemon_index < len(team) and team[pokemon_index].is_alive():
            self.state.set_active_index(player_id, pokemon_index)
            self._log(
                f"  P{player_id} cambia a {team[pokemon_index].name}!"
            )

    def _auto_replace(self, player_id: int):
        active = self.state.get_active(player_id)
        if not active.is_alive():
            idx = self.state.next_alive_index(player_id)
            if idx >= 0:
                self.state.set_active_index(player_id, idx)
                new_pokemon = self.state.get_active(player_id)
                self._log(f"  P{player_id} envía a {new_pokemon.name}!")

    def get_log(self) -> list[str]:
        return self.log

    # ---- helpers usados por la GUI ----

    def _apply_and_log_action(self, state: BattleState, player_id: int, action: dict) -> list[str]:
        pre = len(self.log)
        if action["type"] == "move":
            self._execute_move(player_id, action["move_index"])
        elif action["type"] == "switch":
            self._execute_switch(player_id, action["pokemon_index"])
        return self.log[pre:]

    def _auto_replace_log(self, state: BattleState, out_log: list[str]):
        for pid in (1, 2):
            active = state.get_active(pid)
            if not active.is_alive():
                idx = state.next_alive_index(pid)
                if idx >= 0:
                    state.set_active_index(pid, idx)
                    new_p = state.get_active(pid)
                    msg = f"  P{pid} envía a {new_p.name}!"
                    self.log.append(msg)
                    out_log.append(msg)
