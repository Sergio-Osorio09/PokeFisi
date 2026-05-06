import random
from config import K

# Tabla de efectividad de tipos: chart[ataque][defensa] -> multiplicador
TYPE_CHART: dict[str, dict[str, float]] = {
    "Fire": {
        "Grass": 2.0, "Ice": 2.0, "Bug": 2.0,
        "Water": 0.5, "Fire": 0.5, "Rock": 0.5, "Dragon": 0.5,
    },
    "Water": {
        "Fire": 2.0, "Ground": 2.0, "Rock": 2.0,
        "Water": 0.5, "Grass": 0.5, "Dragon": 0.5,
    },
    "Electric": {
        "Water": 2.0, "Flying": 2.0,
        "Electric": 0.5, "Grass": 0.5, "Dragon": 0.5,
        "Ground": 0.0,
    },
    "Grass": {
        "Water": 2.0, "Ground": 2.0, "Rock": 2.0,
        "Fire": 0.5, "Grass": 0.5, "Poison": 0.5,
        "Flying": 0.5, "Bug": 0.5, "Dragon": 0.5,
    },
    "Psychic": {
        "Fighting": 2.0, "Poison": 2.0,
        "Psychic": 0.5,
        "Dark": 0.0,
    },
    "Ghost": {
        "Ghost": 2.0, "Psychic": 2.0,
        "Normal": 0.0, "Dark": 0.0,
    },
    "Fighting": {
        "Normal": 2.0, "Ice": 2.0, "Rock": 2.0, "Dark": 2.0,
        "Poison": 0.5, "Bug": 0.5, "Psychic": 0.5, "Flying": 0.5, "Fairy": 0.5,
        "Ghost": 0.0,
    },
    "Dragon": {
        "Dragon": 2.0,
        "Steel": 0.5,
        "Fairy": 0.0,
    },
    "Ice": {
        "Grass": 2.0, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0,
        "Water": 0.5, "Ice": 0.5,
    },
    "Ground": {
        "Fire": 2.0, "Electric": 2.0, "Poison": 2.0, "Rock": 2.0, "Steel": 2.0,
        "Grass": 0.5, "Bug": 0.5,
        "Flying": 0.0,
    },
    "Rock": {
        "Fire": 2.0, "Ice": 2.0, "Flying": 2.0, "Bug": 2.0,
        "Fighting": 0.5, "Ground": 0.5, "Steel": 0.5,
    },
    "Flying": {
        "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0,
        "Electric": 0.5, "Rock": 0.5, "Steel": 0.5,
    },
    "Bug": {
        "Grass": 2.0, "Psychic": 2.0, "Dark": 2.0,
        "Fire": 0.5, "Fighting": 0.5, "Flying": 0.5,
        "Ghost": 0.5, "Steel": 0.5, "Fairy": 0.5,
    },
    "Normal": {
        "Rock": 0.5, "Steel": 0.5,
        "Ghost": 0.0,
    },
    "Poison": {
        "Grass": 2.0, "Fairy": 2.0,
        "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5,
        "Steel": 0.0,
    },
    "Fairy": {
        "Fighting": 2.0, "Dragon": 2.0, "Dark": 2.0,
        "Fire": 0.5, "Poison": 0.5, "Steel": 0.5,
    },
}


def get_type_multiplier(attack_type: str, defender_types: list[str]) -> float:
    multiplier = 1.0
    chart = TYPE_CHART.get(attack_type, {})
    for def_type in defender_types:
        multiplier *= chart.get(def_type, 1.0)
    return multiplier


def calculate_damage(attacker, move, defender) -> tuple[int, float]:
    """
    Fórmula del documento:
        Damage = (Attack / Defense_op) * BasePower - Speed_op * K

    Retorna (damage_dealt, type_multiplier).
    damage_dealt == 0 si el ataque falla.
    """
    # Verificar precisión
    if random.randint(1, 100) > move.accuracy:
        return 0, 1.0

    raw = (attacker.attack / max(1, defender.defense)) * move.base_power - defender.speed * K
    raw = max(1, raw)  # daño mínimo 1

    multiplier = get_type_multiplier(move.type, defender.types)
    final = int(raw * multiplier)
    final = max(0, final)  # inmunidad total → 0

    return final, multiplier
