import random
from engine.move import Move


def battle_stats(stats: dict) -> dict:
    """Estadisticas reales de combate (nivel 100) a partir de las base del JSON.

    Fuente unica de la formula: la usan tanto el combate (Pokemon.__init__)
    como las pantallas de seleccion, para que siempre coincidan.
    """
    return {
        "hp":      2 * stats["hp"]      + 110,
        "attack":  2 * stats["attack"]  + 5,
        "defense": 2 * stats["defense"] + 5,
        "speed":   2 * stats["speed"]   + 5,
    }


class Pokemon:
    def __init__(self, data: dict, all_moves: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.types = data["types"]
        self.image      = data.get("image", "")
        self.image_back = data.get("image_back", "")

        bs = battle_stats(data["stats"])
        self.max_hp  = bs["hp"]
        self.current_hp = self.max_hp
        self.attack  = bs["attack"]
        self.defense = bs["defense"]
        self.speed   = bs["speed"]

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
