import json
import os
from engine.move import Move
from engine.pokemon import Pokemon


def load_moves(path: str = "data/moves.json") -> dict[int, Move]:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {m["id"]: Move(m) for m in raw}


def load_all_pokemon(path: str = "data/pokemon.json") -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_team(pokemon_ids: list[int], all_moves: dict) -> list[Pokemon]:
    pokemon_data = load_all_pokemon()
    by_id = {p["id"]: p for p in pokemon_data}
    return [Pokemon(by_id[pid], all_moves) for pid in pokemon_ids if pid in by_id]
