import random
from engine.move import Move


class Pokemon:
    def __init__(self, data: dict, all_moves: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.types = data["types"]
        self.image = data.get("image", "")

        stats = data["stats"]
        self.max_hp  = 2 * stats["hp"]      + 110
        self.current_hp = self.max_hp
        self.attack  = 2 * stats["attack"]  + 5
        self.defense = 2 * stats["defense"] + 5
        self.speed   = 2 * stats["speed"]   + 5

        move_ids = data["move_ids"]
        available = [all_moves[mid] for mid in move_ids if mid in all_moves]
        # Selecciona hasta 4 movimientos para la batalla
        self.moves = random.sample(available, min(4, len(available)))

    def is_alive(self) -> bool:
        return self.current_hp > 0

    def take_damage(self, amount: int):
        self.current_hp = max(0, self.current_hp - amount)

    def heal(self, amount: int):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def reset(self):
        self.current_hp = self.max_hp

    def get_available_moves(self) -> list:
        return self.moves

    def hp_ratio(self) -> float:
        return self.current_hp / self.max_hp

    def __repr__(self):
        return f"Pokemon({self.name}, HP:{self.current_hp}/{self.max_hp})"
