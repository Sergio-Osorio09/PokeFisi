import pygame
from config import WHITE
from gui import theme


class Button:
    def __init__(self, rect: tuple, text: str, font_size: int = 22,
                 color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER,
                 text_color=WHITE, border_radius: int = 12):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.font = theme.font(font_size, "semibold")
        self._hovered = False
        self.enabled = True

    def draw(self, surface: pygame.Surface):
        r = self.rect
        if not self.enabled:
            base = theme.SURFACE_LIGHT
            txt_col = theme.TEXT_DIM
        else:
            base = self.hover_color if self._hovered else self.color
            txt_col = self.text_color

        # Sombra suave bajo el botón
        if self.enabled:
            sh = pygame.Surface((r.w + 20, r.h + 20), pygame.SRCALPHA)
            pygame.draw.rect(sh, (0, 0, 0, 90), (10, 12, r.w, r.h),
                             border_radius=self.border_radius)
            surface.blit(sh, (r.x - 10, r.y - 10))

        # Relleno con degradado vertical sutil (claro arriba -> base abajo)
        top = theme.lerp(base, (255, 255, 255), 0.12)
        theme.vgradient_rect(surface, r, top, base, radius=self.border_radius)

        # Brillo superior tenue al pasar el ratón
        if self._hovered and self.enabled:
            pygame.draw.rect(surface, theme.lerp(base, (255, 255, 255), 0.25),
                             r, 2, border_radius=self.border_radius)

        label = self.font.render(self.text, True, txt_col)
        surface.blit(label, label.get_rect(center=r.center))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                return True
        return False
