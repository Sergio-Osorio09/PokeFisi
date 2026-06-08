"""
Pantalla de selección para el modo Torneo de IAs.
Eliges qué IAs participan y cuántas de cada una (total = 2, 4 u 8).
"""
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from gui import comic, theme
from gui.components.button import Button
from ai import registry
from arena import core

ROW_Y0 = 122
ROW_H = 44
VALID_TOTALS = (2, 4, 8)
MAX_TOTAL = 8


def _stepper_box(surface, rect, ch, enabled=True):
    fill = comic.GOLD if enabled else comic.SLATE
    pygame.draw.rect(surface, comic.INK, rect.move(3, 3), border_radius=6)
    pygame.draw.rect(surface, fill, rect, border_radius=6)
    pygame.draw.rect(surface, comic.INK, rect, 3, border_radius=6)
    comic.outlined_text(surface, ch, 22, rect.center, fill=comic.INK,
                        outline=comic.INK, ow=1, weight="bold")


class TournamentSelect:
    def __init__(self):
        registry.refresh_registry()
        self.reg = registry.AI_REGISTRY
        self.counts = [0] * len(self.reg)
        cx = WINDOW_WIDTH // 2
        self.btn_back  = Button((cx - 250, WINDOW_HEIGHT - 62, 180, 48), "ATRAS",
                                font_size=20, color=comic.RED, hover_color=comic.RED_HOVER,
                                style="comic")
        self.btn_start = Button((cx + 70, WINDOW_HEIGHT - 62, 180, 48), "INICIAR",
                                font_size=20, color=comic.GREEN, hover_color=comic.GREEN_HOVER,
                                style="comic")
        self._minus = []   # rects por fila
        self._plus = []

    def _total(self):
        return sum(self.counts)

    def update(self, dt: int = 0):
        pass

    # ── draw ─────────────────────────────────────────────────────────────────
    def draw(self, surface):
        comic.sub_background(surface)
        cx = WINDOW_WIDTH // 2
        comic.title(surface, "Torneo de IAs", (cx, 46), size=32)
        comic.outlined_text(
            surface, "Elige las IAs y cuantas de cada una. El total debe ser 2, 4 u 8.",
            15, (cx, 84), fill=comic.PAPER, outline=comic.INK, ow=2, weight="semibold")

        list_x, list_w = 70, WINDOW_WIDTH - 140
        self._minus, self._plus = [], []
        for i, (name, _) in enumerate(self.reg):
            y = ROW_Y0 + i * ROW_H
            rect = pygame.Rect(list_x, y, list_w, ROW_H - 6)
            sel = self.counts[i] > 0
            comic.panel(surface, rect, fill=(46, 110, 70) if sel else comic.PANEL_FILL,
                        radius=8, border_w=3, shadow=False)
            # nombre (izquierda, con contorno)
            lab = comic.make_label(name, 16, fill=comic.PAPER, outline=comic.INK, ow=1, weight="semibold")
            surface.blit(lab, lab.get_rect(midleft=(rect.x + 14, rect.centery)))
            # stepper a la derecha:  [-]  N  [+]
            mx = rect.right - 150
            minus = pygame.Rect(mx, y + 3, 32, ROW_H - 12)
            plus  = pygame.Rect(mx + 108, y + 3, 32, ROW_H - 12)
            self._minus.append(minus)
            self._plus.append(plus)
            _stepper_box(surface, minus, "-", enabled=self.counts[i] > 0)
            _stepper_box(surface, plus, "+", enabled=self._total() < MAX_TOTAL)
            comic.outlined_text(surface, str(self.counts[i]), 22, (mx + 70, rect.centery),
                                fill=comic.SUN1, outline=comic.INK, ow=2, weight="bold")

        # total + validez
        total = self._total()
        valid = total in VALID_TOTALS
        msg = "listo para iniciar" if valid else "debe ser 2, 4 u 8"
        comic.outlined_text(surface, f"Total: {total}   ({msg})", 19,
                            (cx, WINDOW_HEIGHT - 100),
                            fill=comic.GREEN if valid else comic.SUN2,
                            outline=comic.INK, ow=2, weight="bold")
        comic.outlined_text(surface, "Excluidos por desbalance: Mewtwo, Dragonite, Cloyster, Snorlax",
                            12, (cx, WINDOW_HEIGHT - 78), fill=comic.PAPER,
                            outline=comic.INK, ow=1, weight="regular")

        self.btn_back.draw(surface)
        self.btn_start.enabled = valid
        self.btn_start.draw(surface)

    # ── eventos ──────────────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.reg)):
                if i < len(self._minus) and self._minus[i].collidepoint(event.pos):
                    self.counts[i] = max(0, self.counts[i] - 1)
                    return None
                if i < len(self._plus) and self._plus[i].collidepoint(event.pos):
                    if self._total() < MAX_TOTAL:
                        self.counts[i] += 1
                    return None

        if self.btn_back.handle_event(event):
            return "MENU"
        if self.btn_start.handle_event(event) and self._total() in VALID_TOTALS:
            selection = [(i, c) for i, c in enumerate(self.counts) if c > 0]
            competitors = core.registry_competitors(selection)
            return ("TOURNAMENT", competitors)
        return None
