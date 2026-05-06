import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from gui.assets_loader import get_font
from gui.components.button import Button


class MainMenu:
    def __init__(self):
        self.font_title = get_font(64)
        self.font_sub = get_font(18)
        cx = WINDOW_WIDTH // 2
        bw, bh = 280, 52
        self.btn_battle = Button((cx - bw//2, 320, bw, bh), "NUEVA BATALLA", font_size=24, color=(40,100,40), hover_color=(60,150,60))
        self.btn_exit   = Button((cx - bw//2, 410, bw, bh), "SALIR",         font_size=24, color=(120,30,30), hover_color=(180,50,50))

    def update(self, dt: int = 0):
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(BG_COLOR)

        title = self.font_title.render("POKEFISI", True, (255, 220, 0))
        surface.blit(title, title.get_rect(centerx=WINDOW_WIDTH//2, top=120))

        sub = self.font_sub.render("Simulador de Combates con IA", True, WHITE)
        surface.blit(sub, sub.get_rect(centerx=WINDOW_WIDTH//2, top=210))

        self.btn_battle.draw(surface)
        self.btn_exit.draw(surface)

    def handle_event(self, event: pygame.event.Event):
        if self.btn_battle.handle_event(event):
            return "MODE_SELECT"
        if self.btn_exit.handle_event(event):
            return "QUIT"
        return None
