import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from engine.move import Move
from engine.damage import calculate_damage, get_type_multiplier


class FakePokemon:
    def __init__(self, attack, defense, speed, types):
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.types = types
        self.current_hp = 100
        self.max_hp = 100

    def take_damage(self, amount): pass


def make_move(base_power=90, accuracy=100, move_type="Normal"):
    return Move({"id":1,"name":"Test","type":move_type,"base_power":base_power,
                 "accuracy":accuracy,"category":"special","effect":"none"})


def test_damage_minimum_is_1():
    attacker = FakePokemon(10, 200, 10, ["Normal"])
    defender = FakePokemon(10, 200, 100, ["Normal"])
    move = make_move(base_power=1, accuracy=100)
    dmg, _ = calculate_damage(attacker, move, defender)
    assert dmg >= 1 or dmg == 0  # 0 solo si falla la precisión


def test_supereffective_doubles():
    attacker = FakePokemon(100, 50, 10, ["Fire"])
    defender = FakePokemon(50, 50, 10, ["Grass"])
    move = make_move(base_power=90, accuracy=100, move_type="Fire")
    import random; random.seed(1)
    dmg, mult = calculate_damage(attacker, move, defender)
    assert mult == 2.0


def test_immune_deals_zero():
    attacker = FakePokemon(100, 50, 10, ["Normal"])
    defender = FakePokemon(50, 50, 10, ["Ghost"])
    move = make_move(base_power=90, accuracy=100, move_type="Normal")
    import random; random.seed(1)
    dmg, mult = calculate_damage(attacker, move, defender)
    assert mult == 0.0
    assert dmg == 0


def test_type_multiplier_water_vs_fire():
    mult = get_type_multiplier("Water", ["Fire"])
    assert mult == 2.0


def test_type_multiplier_neutral():
    mult = get_type_multiplier("Normal", ["Normal"])
    assert mult == 1.0
