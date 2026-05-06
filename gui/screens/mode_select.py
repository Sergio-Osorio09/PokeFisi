import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from gui.assets_loader import get_font
from gui.components.button import Button


class ModeSelect:
    def __init__(self):
        self.font_title = get_font(40)
        self.font_label = get_font(18)
        cx = WINDOW_WIDTH // 2

        # Botones de modo
        self.btn_human = Button((cx - 310, 180, 280, 80), "HUMANO vs IA",
                                font_size=22, color=(40,90,160), hover_color=(60,130,200))
        self.btn_ai    = Button((cx + 30,  180, 280, 80), "IA vs IA",
                                font_size=22, color=(120,40,120), hover_color=(170,60,170))

        # Selector de IA (ai2 siempre visible, ai1 solo en ai_vs_ai)
        self.ai_options = ["Agente Aleatorio", "Heuristica Basica"]
        self.ai1_idx = 0
        self.ai2_idx = 0

        # Botones selector IA1 (ai_vs_ai)
        self.btn_ai1_prev = Button((cx - 290, 360, 36, 36), "<", font_size=18)
        self.btn_ai1_next = Button((cx - 70,  360, 36, 36), ">", font_size=18)

        # Botones selector IA2 (ambos modos)
        self.btn_ai2_prev = Button((cx + 50,  360, 36, 36), "<", font_size=18)
        self.btn_ai2_next = Button((cx + 270, 360, 36, 36), ">", font_size=18)

        # Tamaño de equipo
        self.team_size = 3
        self.btn_size3 = Button((cx - 110, 470, 90, 40), "3 vs 3",
                                font_size=18, color=(50,80,50), hover_color=(70,120,70))
        self.btn_size4 = Button((cx + 20,  470, 90, 40), "4 vs 4",
                                font_size=18, color=(50,80,50), hover_color=(70,120,70))

        # Navegación
        self.btn_back  = Button((cx - 160, 560, 140, 46), "ATRAS",
                                font_size=20, color=(100,40,40), hover_color=(150,60,60))
        self.btn_start = Button((cx + 20,  560, 140, 46), "CONTINUAR",
                                font_size=20, color=(40,100,40), hover_color=(60,150,60))

        self.mode = None

    def draw(self, surface: pygame.Surface):
        surface.fill(BG_COLOR)
        cx = WINDOW_WIDTH // 2

        title = self.font_title.render("Modo de Juego", True, (255, 220, 0))
        surface.blit(title, title.get_rect(centerx=cx, top=90))

        self.btn_human.draw(surface)
        self.btn_ai.draw(surface)

        # Resaltar modo seleccionado
        if self.mode == "human_vs_ai":
            pygame.draw.rect(surface, (255, 220, 0), self.btn_human.rect, 3, border_radius=10)
        elif self.mode == "ai_vs_ai":
            pygame.draw.rect(surface, (255, 220, 0), self.btn_ai.rect, 3, border_radius=10)

        # ── Selectores de IA ──────────────────────────────────────────────
        if self.mode == "ai_vs_ai":
            # IA 1 (izquierda)
            lbl1 = self.font_label.render("IA Jugador 1:", True, WHITE)
            surface.blit(lbl1, (cx - 290, 330))
            self.btn_ai1_prev.draw(surface)
            self.btn_ai1_next.draw(surface)
            ai1_txt = self.font_label.render(self.ai_options[self.ai1_idx], True, (180, 220, 255))
            surface.blit(ai1_txt, (cx - 248, 365))

            # IA 2 (derecha)
            lbl2 = self.font_label.render("IA Jugador 2:", True, WHITE)
            surface.blit(lbl2, (cx + 50, 330))
            self.btn_ai2_prev.draw(surface)
            self.btn_ai2_next.draw(surface)
            ai2_txt = self.font_label.render(self.ai_options[self.ai2_idx], True, (255, 200, 255))
            surface.blit(ai2_txt, (cx + 92, 365))

        elif self.mode == "human_vs_ai":
            # Solo IA rival, centrada
            lbl = self.font_label.render("IA rival:", True, WHITE)
            surface.blit(lbl, lbl.get_rect(centerx=cx, top=330))

            # Reutilizamos btn_ai2_prev / next centrados
            prev_rect = pygame.Rect(cx - 140, 358, 36, 36)
            next_rect = pygame.Rect(cx + 104, 358, 36, 36)
            self.btn_ai2_prev.rect = prev_rect
            self.btn_ai2_next.rect = next_rect
            self.btn_ai2_prev.draw(surface)
            self.btn_ai2_next.draw(surface)
            ai2_txt = self.font_label.render(self.ai_options[self.ai2_idx], True, (255, 200, 100))
            surface.blit(ai2_txt, ai2_txt.get_rect(centerx=cx, top=365))

        # ── Tamaño de equipo ──────────────────────────────────────────────
        size_lbl = self.font_label.render(f"Tamaño de equipo:", True, WHITE)
        surface.blit(size_lbl, size_lbl.get_rect(centerx=cx, top=440))
        self.btn_size3.draw(surface)
        self.btn_size4.draw(surface)
        if self.team_size == 3:
            pygame.draw.rect(surface, (255, 220, 0), self.btn_size3.rect, 3, border_radius=10)
        else:
            pygame.draw.rect(surface, (255, 220, 0), self.btn_size4.rect, 3, border_radius=10)

        self.btn_back.draw(surface)
        self.btn_start.enabled = self.mode is not None
        self.btn_start.draw(surface)

    def handle_event(self, event: pygame.event.Event):
        n = len(self.ai_options)

        if self.btn_human.handle_event(event):
            self.mode = "human_vs_ai"
        if self.btn_ai.handle_event(event):
            self.mode = "ai_vs_ai"

        if self.btn_ai1_prev.handle_event(event):
            self.ai1_idx = (self.ai1_idx - 1) % n
        if self.btn_ai1_next.handle_event(event):
            self.ai1_idx = (self.ai1_idx + 1) % n
        if self.btn_ai2_prev.handle_event(event):
            self.ai2_idx = (self.ai2_idx - 1) % n
        if self.btn_ai2_next.handle_event(event):
            self.ai2_idx = (self.ai2_idx + 1) % n

        if self.btn_size3.handle_event(event):
            self.team_size = 3
        if self.btn_size4.handle_event(event):
            self.team_size = 4

        if self.btn_back.handle_event(event):
            return "MENU"
        if self.btn_start.handle_event(event) and self.mode:
            return ("POKEMON_SELECT", self.mode, self.team_size, self.ai1_idx, self.ai2_idx)
        return None
