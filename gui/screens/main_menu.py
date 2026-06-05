import pygame
from config import WHITE, WINDOW_WIDTH, WINDOW_HEIGHT
from gui import theme
from gui.components.button import Button


def _draw_pokeball(surface, cx, cy, r):
    """Dibuja un pokeball minimalista centrado en (cx, cy)."""
    band_h = max(4, int(r * 0.20))
    # base blanca (mitad inferior)
    pygame.draw.circle(surface, (236, 239, 246), (cx, cy), r)
    # mitad superior roja (recortando con clip)
    prev = surface.get_clip()
    surface.set_clip(pygame.Rect(cx - r, cy - r, 2 * r, r))
    pygame.draw.circle(surface, theme.DANGER, (cx, cy), r)
    surface.set_clip(prev)
    # banda central
    pygame.draw.rect(surface, (24, 26, 38), (cx - r, cy - band_h // 2, 2 * r, band_h))
    # contorno
    pygame.draw.circle(surface, (24, 26, 38), (cx, cy), r, 3)
    # botón central
    pygame.draw.circle(surface, (24, 26, 38), (cx, cy), int(r * 0.30))
    pygame.draw.circle(surface, (236, 239, 246), (cx, cy), int(r * 0.20))
    pygame.draw.circle(surface, (24, 26, 38), (cx, cy), int(r * 0.20), 2)


class MainMenu:
    def __init__(self):
        cx = WINDOW_WIDTH // 2
        bw, bh = 330, 56
        x = cx - bw // 2
        self.btn_battle = Button((x, 352, bw, bh), "NUEVA BATALLA",
                                 font_size=22, color=theme.SUCCESS, hover_color=theme.SUCCESS_HOVER)
        self.btn_train  = Button((x, 422, bw, bh), "ENTRENAR IA GENÉTICA",
                                 font_size=20, color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER)
        self.btn_delete = Button((x, 492, bw, bh), "ELIMINAR IAS ENTRENADAS",
                                 font_size=18, color=theme.SURFACE_LIGHT, hover_color=theme.BORDER,
                                 text_color=theme.TEXT_MUTED)
        self.btn_exit   = Button((x, 562, bw, bh), "SALIR",
                                 font_size=22, color=theme.DANGER, hover_color=theme.DANGER_HOVER)

    def update(self, dt: int = 0):
        pass

    def draw(self, surface: pygame.Surface):
        theme.background(surface)
        cx = WINDOW_WIDTH // 2

        _draw_pokeball(surface, cx, 150, 48)

        theme.text(surface, "PokeFisi", 60, (cx, 250), color=WHITE,
                   weight="bold", center=True)
        theme.text(surface, "Simulador de combates con Inteligencia Artificial",
                   18, (cx, 300), color=theme.TEXT_MUTED, weight="regular", center=True)

        self.btn_battle.draw(surface)
        self.btn_train.draw(surface)
        self.btn_delete.draw(surface)
        self.btn_exit.draw(surface)

        theme.text(surface,
                   "Agentes: Aleatorio · Heurísticas · Minimax (alfa-beta) · Expectimax · Genético",
                   13, (cx, WINDOW_HEIGHT - 30), color=theme.TEXT_DIM,
                   weight="regular", center=True)

    def handle_event(self, event: pygame.event.Event):
        if self.btn_battle.handle_event(event):
            return "MODE_SELECT"
        if self.btn_train.handle_event(event):
            return "TRAIN"
        if self.btn_delete.handle_event(event):
            return "DELETE"
        if self.btn_exit.handle_event(event):
            return "QUIT"
        return None
