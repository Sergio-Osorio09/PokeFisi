import os
import pygame
from config import TYPE_COLORS


_cache: dict = {}


def get_font(size: int, weight: str = "medium") -> pygame.font.Font:
    """Fuente del tema (Poppins). Delega en gui.theme para mantener una sola
    tipografía coherente en toda la interfaz."""
    from gui import theme
    return theme.font(size, weight)


def get_pokemon_image(image_path: str, size: tuple = (80, 80)) -> pygame.Surface:
    key = f"img_{image_path}_{size}"
    if key not in _cache:
        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            _cache[key] = pygame.transform.scale(img, size)
        else:
            # Placeholder: círculo de color según tipo
            surf = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (150, 150, 180), (0, 0, size[0], size[1]))
            pygame.draw.ellipse(surf, (100, 100, 130), (0, 0, size[0], size[1]), 2)
            # "P" centrado
            font = get_font(max(12, size[0] // 4))
            label = font.render("?", True, (255, 255, 255))
            surf.blit(label, label.get_rect(center=(size[0]//2, size[1]//2)))
            _cache[key] = surf
    return _cache[key]


def get_type_color(type_name: str) -> tuple:
    return TYPE_COLORS.get(type_name, (150, 150, 150))
