import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from gui.assets_loader import get_font
from gui.components.button import Button


class ResultsScreen:
    def __init__(self, winner: int, state):
        self.winner = winner
        self.state = state
        self.font_big   = get_font(52)
        self.font_mid   = get_font(26)
        self.font_small = get_font(18)
        cx = WINDOW_WIDTH // 2
        self.btn_menu    = Button((cx - 160, 500, 140, 50), "MENU",     font_size=22, color=(40,80,160), hover_color=(60,120,200))
        self.btn_rematch = Button((cx + 20,  500, 140, 50), "REVANCHA", font_size=22, color=(40,100,40), hover_color=(60,150,60))

    def draw(self, surface: pygame.Surface):
        surface.fill(BG_COLOR)

        winner_color = (255, 220, 0) if self.winner == 1 else (200, 120, 255)
        title = self.font_big.render(
            f"¡Jugador {self.winner} gana!" if self.winner else "¡Empate!",
            True, winner_color)
        surface.blit(title, title.get_rect(centerx=WINDOW_WIDTH//2, top=150))

        # Stats
        turn_lbl = self.font_mid.render(f"Turnos jugados: {self.state.turn_number}", True, WHITE)
        surface.blit(turn_lbl, turn_lbl.get_rect(centerx=WINDOW_WIDTH//2, top=260))

        alive1 = sum(1 for p in self.state.player1_team if p.is_alive())
        alive2 = sum(1 for p in self.state.player2_team if p.is_alive())
        t1 = self.font_small.render(f"Jugador 1 — Pokémon en pie: {alive1}", True, (180,220,180))
        t2 = self.font_small.render(f"Jugador 2 — Pokémon en pie: {alive2}", True, (220,180,220))
        surface.blit(t1, t1.get_rect(centerx=WINDOW_WIDTH//2, top=320))
        surface.blit(t2, t2.get_rect(centerx=WINDOW_WIDTH//2, top=350))

        self.btn_menu.draw(surface)
        self.btn_rematch.draw(surface)

    def handle_event(self, event: pygame.event.Event):
        if self.btn_menu.handle_event(event):
            return "MENU"
        if self.btn_rematch.handle_event(event):
            return "MODE_SELECT"
        return None
