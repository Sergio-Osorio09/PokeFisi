import copy as _copy


class BattleState:
    def __init__(self, team1: list, team2: list):
        self.player1_team = team1
        self.player2_team = team2
        self.active_index_p1 = 0
        self.active_index_p2 = 0
        self.turn_number = 0

    @property
    def active_pokemon_p1(self):
        return self.player1_team[self.active_index_p1]

    @property
    def active_pokemon_p2(self):
        return self.player2_team[self.active_index_p2]

    def get_team(self, player_id: int) -> list:
        return self.player1_team if player_id == 1 else self.player2_team

    def get_active(self, player_id: int):
        return self.active_pokemon_p1 if player_id == 1 else self.active_pokemon_p2

    def get_active_index(self, player_id: int) -> int:
        return self.active_index_p1 if player_id == 1 else self.active_index_p2

    def set_active_index(self, player_id: int, index: int):
        if player_id == 1:
            self.active_index_p1 = index
        else:
            self.active_index_p2 = index

    def alive_team(self, player_id: int) -> list:
        return [p for p in self.get_team(player_id) if p.is_alive()]

    def next_alive_index(self, player_id: int) -> int:
        for i, p in enumerate(self.get_team(player_id)):
            if p.is_alive():
                return i
        return -1

    def is_terminal(self) -> bool:
        return (
            all(not p.is_alive() for p in self.player1_team)
            or all(not p.is_alive() for p in self.player2_team)
        )

    def get_winner(self):
        p1_alive = any(p.is_alive() for p in self.player1_team)
        p2_alive = any(p.is_alive() for p in self.player2_team)
        if p1_alive and not p2_alive:
            return 1
        if p2_alive and not p1_alive:
            return 2
        return None

    def copy(self):
        """Clon ligero para simulaciones (minimax / heurísticas).

        Durante una simulación lo único que se muta es ``current_hp`` de cada
        Pokémon y los índices de activo. El resto (tipos, movimientos, stats)
        es inmutable, así que basta una copia superficial de cada Pokémon
        compartiendo esos datos: ~10-50x más rápido que ``deepcopy`` y
        suficiente para que la simulación no corrompa el estado original.
        """
        new = BattleState.__new__(BattleState)
        new.player1_team = [_copy.copy(p) for p in self.player1_team]
        new.player2_team = [_copy.copy(p) for p in self.player2_team]
        new.active_index_p1 = self.active_index_p1
        new.active_index_p2 = self.active_index_p2
        new.turn_number = self.turn_number
        return new

    def __repr__(self):
        return (
            f"Turn {self.turn_number} | "
            f"P1: {self.active_pokemon_p1} | "
            f"P2: {self.active_pokemon_p2}"
        )
