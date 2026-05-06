import pygame
from config import WHITE, DARK
from gui.assets_loader import get_font


class BattleLog:
    def __init__(self, x: int, y: int, width: int, height: int, max_lines: int = 8):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = get_font(14)
        self.lines: list[str] = []
        self.max_lines = max_lines

    def add(self, text: str):
        self.lines.append(text)
        if len(self.lines) > self.max_lines * 3:
            self.lines = self.lines[-self.max_lines * 3:]

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (20, 20, 35), self.rect, border_radius=6)
        pygame.draw.rect(surface, (80, 80, 120), self.rect, 1, border_radius=6)

        visible = self.lines[-self.max_lines:]
        line_h = self.font.get_linesize()
        for i, line in enumerate(visible):
            color = (220, 220, 120) if line.startswith("===") else WHITE
            surf = self.font.render(line[:60], True, color)
            surface.blit(surf, (self.rect.x + 6, self.rect.y + 6 + i * line_h))
