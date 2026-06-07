"""
Pantalla para eliminar IAs entrenadas (pesos guardados en data/):
HeuristicaAvanzada-N, H.Mejorada-N y Genetico g/p/d. Tras borrar, refresca el
registro para que el agente desaparezca de los selectores sin reiniciar.
"""
import os
import json

import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from gui.assets_loader import get_font
from gui.components.button import Button
from gui import comic


def _gather_trained() -> list[tuple]:
    """Devuelve [(ruta, etiqueta)] de todas las IAs entrenadas en data/."""
    from ai.heuristic_trained import find_trained_weights
    from ai.heuristic_improved import find_improved_weights
    from ai.genetic_trainer import find_genetic_weights

    items = []
    for p in find_trained_weights():
        try:
            d = json.load(open(p, encoding="utf-8"))
            items.append((p, f"HeuristicaAvanzada-{d.get('battles','?')}"
                             f"  (WR {d.get('win_rate',0):.0%})"))
        except Exception:
            items.append((p, os.path.basename(p)))
    for p in find_improved_weights():
        try:
            d = json.load(open(p, encoding="utf-8"))
            items.append((p, f"H.Mejorada-{d.get('battles','?')}"
                             f"  (WR {d.get('win_rate',0):.0%})"))
        except Exception:
            items.append((p, os.path.basename(p)))
    for p in find_genetic_weights():
        try:
            d = json.load(open(p, encoding="utf-8"))
            items.append((p, f"Genetico g={d.get('generations','?')} "
                             f"p={d.get('pop_size','?')} d={d.get('minimax_depth',2)}"
                             f"  (fit {d.get('fitness',0):.0%})"))
        except Exception:
            items.append((p, os.path.basename(p)))
    return items


class DeleteScreen:
    ROW_Y0, ROW_STEP = 130, 46

    def __init__(self):
        self.font_title = get_font(34)
        self.font_row   = get_font(16)
        self.font_info  = get_font(15)
        cx = WINDOW_WIDTH // 2

        self.btn_back = Button((cx - 90, WINDOW_HEIGHT - 70, 180, 46), "ATRAS",
                               font_size=20, color=(100, 40, 40), hover_color=(150, 60, 60))

        # Confirmación (modal)
        self._pending = None          # (ruta, etiqueta) a eliminar
        self._message = None          # texto temporal de feedback
        bw, bh = 150, 46
        self.btn_yes = Button((cx - bw - 12, WINDOW_HEIGHT // 2 + 10, bw, bh), "ELIMINAR",
                              font_size=18, color=(150, 50, 50), hover_color=(200, 70, 70))
        self.btn_no  = Button((cx + 12, WINDOW_HEIGHT // 2 + 10, bw, bh), "CANCELAR",
                              font_size=18, color=(60, 90, 60), hover_color=(80, 130, 80))

        self._rows = []   # [(ruta, etiqueta, boton_eliminar)]
        self._refresh()

    def _refresh(self):
        self._rows = []
        for i, (path, label) in enumerate(_gather_trained()):
            y = self.ROW_Y0 + i * self.ROW_STEP
            btn = Button((WINDOW_WIDTH - 200, y, 150, 32), "Eliminar",
                         font_size=15, color=(130, 50, 50), hover_color=(180, 70, 70))
            self._rows.append((path, label, btn))

    # ── update / draw ──────────────────────────────────────────────────────

    def update(self, dt: int = 0):
        pass

    def draw(self, surface: pygame.Surface):
        comic.sub_background(surface)
        cx = WINDOW_WIDTH // 2

        comic.title(surface, "Eliminar IAs entrenadas", (cx, 72), size=34)

        if not self._rows:
            msg = self.font_info.render("No hay IAs entrenadas guardadas.", True, (180, 180, 200))
            surface.blit(msg, msg.get_rect(centerx=cx, top=140))
        else:
            sub = self.font_info.render(
                "Selecciona una IA para eliminar su archivo de pesos.", True, (170, 170, 190))
            surface.blit(sub, sub.get_rect(centerx=cx, top=98))
            for path, label, btn in self._rows:
                ry = btn.rect.y
                comic.panel(surface, (50, ry - 6, WINDOW_WIDTH - 100, self.ROW_STEP - 8),
                            radius=8, border_w=3, shadow=False)
                ls = self.font_row.render(label, True, WHITE)
                surface.blit(ls, (66, ry + 2))
                btn.draw(surface)

        if self._message:
            ms = self.font_info.render(self._message, True, (150, 220, 150))
            surface.blit(ms, ms.get_rect(centerx=cx, bottom=WINDOW_HEIGHT - 78))

        self.btn_back.draw(surface)

        # Modal de confirmación
        if self._pending is not None:
            self._draw_confirm(surface)

    def _draw_confirm(self, surface):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        cx = WINDOW_WIDTH // 2
        bw, bh = 560, 180
        bx, by = cx - bw // 2, WINDOW_HEIGHT // 2 - bh // 2
        comic.panel(surface, (bx, by, bw, bh), fill=(34, 44, 116), radius=12, border_w=4)

        q = self.font_info.render("¿Eliminar esta IA entrenada?", True, WHITE)
        surface.blit(q, q.get_rect(centerx=cx, top=by + 22))
        nm = self.font_row.render(self._pending[1], True, (255, 210, 120))
        surface.blit(nm, nm.get_rect(centerx=cx, top=by + 56))
        self.btn_yes.draw(surface)
        self.btn_no.draw(surface)

    # ── eventos ──────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        # Modal de confirmación: tiene prioridad
        if self._pending is not None:
            if self.btn_yes.handle_event(event):
                self._do_delete(self._pending[0])
                self._pending = None
            elif self.btn_no.handle_event(event):
                self._pending = None
            return None

        for path, label, btn in self._rows:
            if btn.handle_event(event):
                self._pending = (path, label)
                self._message = None
                return None

        if self.btn_back.handle_event(event):
            return "MENU"
        return None

    def _do_delete(self, path: str):
        try:
            os.remove(path)
            self._message = f"Eliminado: {os.path.basename(path)}"
        except OSError as exc:
            self._message = f"Error al eliminar: {exc}"
        # Refrescar registro y lista para que el agente desaparezca del selector.
        from ai import registry
        registry.refresh_registry()
        self._refresh()
