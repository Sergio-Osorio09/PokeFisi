import pygame
from config import RED, GREEN, YELLOW, BLACK, WHITE
from gui.assets_loader import get_font


class HPBar:
    def __init__(self, x: int, y: int, width: int = 200, height: int = 16):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = get_font(13)

    def draw(self, surface: pygame.Surface, current: int, max_hp: int, label: str = ""):
        ratio = current / max_hp if max_hp > 0 else 0
        # Background
        pygame.draw.rect(surface, (60, 60, 60), (self.x, self.y, self.width, self.height), border_radius=4)
        # Bar color
        if ratio > 0.5:
            color = GREEN
        elif ratio > 0.25:
            color = YELLOW
        else:
            color = RED
        bar_w = int(self.width * ratio)
        if bar_w > 0:
            pygame.draw.rect(surface, color, (self.x, self.y, bar_w, self.height), border_radius=4)
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height), 1, border_radius=4)

        if label:
            txt = self.font.render(label, True, WHITE)
            surface.blit(txt, (self.x, self.y - 16))
