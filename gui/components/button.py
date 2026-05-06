import pygame
from config import WHITE, DARK, GRAY
from gui.assets_loader import get_font


class Button:
    def __init__(self, rect: tuple, text: str, font_size: int = 22,
                 color=(70, 70, 120), hover_color=(100, 100, 180),
                 text_color=WHITE, border_radius: int = 10):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.font = get_font(font_size)
        self._hovered = False
        self.enabled = True

    def draw(self, surface: pygame.Surface):
        color = self.hover_color if self._hovered and self.enabled else self.color
        if not self.enabled:
            color = GRAY
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=self.border_radius)
        label = self.font.render(self.text, True, self.text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                return True
        return False
