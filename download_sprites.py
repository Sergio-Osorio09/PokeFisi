"""
Descarga los sprites (front y back) de los Pokemon del juego desde PokeAPI (GitHub).
  front: https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{dex_id}.png
  back:  https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/{dex_id}.png
Guarda cada archivo con el nombre definido en data/pokemon.json (campos "image" e "image_back").
Los que ya existen se omiten, asi que solo descarga lo que falta.
"""
import json
import os
import urllib.request
import time

BASE_URL      = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png"
BASE_URL_BACK = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/{}.png"
ROOT = os.path.dirname(__file__)

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
    "Raichu":     26,
    "Ninetales":  38,
    "Golem":      76,
    "Nidoking":   34,
    "Cloyster":   91,
    "Aerodactyl":142,
    "Sandslash":  28,
    "Primeape":   57,
    "Victreebel": 71,
    "Dodrio":     85,
}


def _fetch(url: str, rel_dest: str, label: str) -> None:
    """Descarga `url` a `rel_dest` (ruta relativa a la raiz). Omite si ya existe."""
    if not rel_dest:
        return
    dest = os.path.join(ROOT, rel_dest)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"      {label:<5} ya existe, omitiendo.")
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"      {label:<5} descargado  ({os.path.getsize(dest)} bytes)")
    except Exception as e:
        print(f"      {label:<5} ERROR: {e}")
    time.sleep(0.1)   # pausa corta para no saturar el servidor


def main():
    with open(os.path.join(ROOT, "data", "pokemon.json"), encoding="utf-8") as f:
        pokemon_list = json.load(f)

    total = len(pokemon_list)

    for i, p in enumerate(pokemon_list, 1):
        name   = p["name"]
        dex_id = POKEDEX_ID.get(name)
        print(f"  [{i:2d}/{total}] {name}  (dex#{dex_id})")

        if dex_id is None:
            print("      SIN ID de Pokedex, omitiendo.")
            continue

        _fetch(BASE_URL.format(dex_id),      p.get("image", ""),      "front")
        _fetch(BASE_URL_BACK.format(dex_id), p.get("image_back", ""), "back")

    print("\nListo. Sprites guardados en assets/images/pokemon/ (y /back).\n")


if __name__ == "__main__":
    main()
