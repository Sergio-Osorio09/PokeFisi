"""
Descarga los sprites de los 30 Pokemon del juego desde PokeAPI (GitHub).
URL base: https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_id}.png
Guarda cada archivo en assets/images/pokemon/ con el nombre definido en data/pokemon.json.
"""
import json
import os
import urllib.request
import time

BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png"
OUT_DIR  = os.path.join(os.path.dirname(__file__), "assets", "images", "pokemon")

# Mapeo: nombre del Pokemon → ID del Pokedex nacional
POKEDEX_ID = {
    "Pikachu":    25,
    "Charizard":   6,
    "Blastoise":   9,
    "Venusaur":    3,
    "Mewtwo":    150,
    "Gengar":     94,
    "Machamp":    68,
    "Alakazam":   65,
    "Dragonite": 149,
    "Lapras":    131,
    "Snorlax":   143,
    "Arcanine":   59,
    "Gyarados":  130,
    "Jolteon":   135,
    "Vaporeon":  134,
    "Flareon":   136,
    "Rhydon":    112,
    "Exeggutor": 103,
    "Starmie":   121,
    "Tauros":    128,
    "Scyther":   123,
    "Pinsir":    127,
    "Electabuzz":125,
    "Magmar":    126,
    "Kangaskhan":115,
    "Mr. Mime":  122,
    "Hitmonlee": 106,
    "Hitmonchan":107,
    "Slowbro":    80,
    "Clefable":   36,
}


def main():
    with open(os.path.join(os.path.dirname(__file__), "data", "pokemon.json")) as f:
        pokemon_list = json.load(f)

    os.makedirs(OUT_DIR, exist_ok=True)
    total = len(pokemon_list)

    for i, p in enumerate(pokemon_list, 1):
        name      = p["name"]
        dest_path = os.path.join(os.path.dirname(__file__), p["image"])

        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            print(f"  [{i:2d}/{total}] {name:<14}  ya existe, omitiendo.")
            continue

        dex_id = POKEDEX_ID.get(name)
        if dex_id is None:
            print(f"  [{i:2d}/{total}] {name:<14}  SIN ID de Pokedex, omitiendo.")
            continue

        url = BASE_URL.format(dex_id)
        try:
            urllib.request.urlretrieve(url, dest_path)
            size = os.path.getsize(dest_path)
            print(f"  [{i:2d}/{total}] {name:<14}  descargado  ({size} bytes)  ← dex#{dex_id}")
        except Exception as e:
            print(f"  [{i:2d}/{total}] {name:<14}  ERROR: {e}")

        time.sleep(0.1)   # pausa corta para no saturar el servidor

    print(f"\nListo. Sprites guardados en: {OUT_DIR}\n")


if __name__ == "__main__":
    main()
