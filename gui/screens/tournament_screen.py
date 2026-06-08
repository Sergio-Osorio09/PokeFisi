"""
Pantalla del Torneo de IAs: bracket eliminatorio (mejor de 3) que se juega en
un hilo de fondo y se va llenando visualmente hasta coronar al campeón.
Guarda un reporte documentado al terminar.
"""
import threading
import time

import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from gui import comic, theme
from gui.components.button import Button
from arena import core, report


def _log2(n: int) -> int:
    r = 0
    while (1 << r) < n:
        r += 1
    return r


class TournamentScreen:
    def __init__(self, competitors):
        self.competitors = competitors           # [(label, factory)]
        self.labels = [c[0] for c in competitors]
        self.N = len(competitors)
        self.R = _log2(self.N)                    # nº de rondas

        cx = WINDOW_WIDTH // 2
        self.btn_back = Button((cx - 90, WINDOW_HEIGHT - 56, 180, 46), "VOLVER",
                               font_size=20, color=comic.BLUE, hover_color=comic.BLUE_HOVER,
                               style="comic")

        # estado compartido con el hilo
        self._lock = threading.Lock()
        self._matches = {}          # (ri, mi) -> match dict
        self.phase = "RUNNING"      # RUNNING | DONE | ERROR
        self.champion = None
        self._report_path = None
        self._error = None

        self._layout = self._compute_layout()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    # ── hilo de fondo ──────────────────────────────────────────────────────────
    def _worker(self):
        try:
            def on_match(ri, mi, match):
                with self._lock:
                    self._matches[(ri, mi)] = match
                time.sleep(0.6)     # pacing para "ver avanzar" el bracket
            br = core.run_bracket(self.competitors, best_of=3, size=3, on_match=on_match)
            jp, mp = report.save_bracket(br, tag="torneo")
            with self._lock:
                self.champion = br["champion"]
                self._report_path = mp
                self.phase = "DONE"
        except Exception as exc:     # pragma: no cover - defensivo
            with self._lock:
                self._error = str(exc)
                self.phase = "ERROR"

    # ── layout del bracket (izquierda → derecha) ───────────────────────────────
    def _compute_layout(self):
        margin_x, box_w, box_h = 24, 200, 38
        top, bot = 130, WINDOW_HEIGHT - 116
        hspan = bot - top
        span_x = WINDOW_WIDTH - 2 * margin_x - box_w
        col_cx = [margin_x + box_w / 2 + (c * span_x / self.R if self.R else 0)
                  for c in range(self.R + 1)]
        cols = [[(col_cx[0], top + (i + 0.5) * (hspan / self.N)) for i in range(self.N)]]
        for c in range(1, self.R + 1):
            prev = [cy for (_, cy) in cols[c - 1]]
            cur = [(prev[2 * j] + prev[2 * j + 1]) / 2 for j in range(len(prev) // 2)]
            cols.append([(col_cx[c], y) for y in cur])
        return {"cols": cols, "box_w": box_w, "box_h": box_h}

    def update(self, dt: int = 0):
        pass

    # ── draw ───────────────────────────────────────────────────────────────────
    def draw(self, surface):
        comic.sub_background(surface)
        cx = WINDOW_WIDTH // 2
        comic.title(surface, "Torneo de IAs", (cx, 42), size=30)

        with self._lock:
            matches = dict(self._matches)
            phase = self.phase
            champion = self.champion
            rpath = self._report_path
            error = self._error

        cols = self._layout["cols"]
        bw, bh = self._layout["box_w"], self._layout["box_h"]

        # conectores
        for c in range(1, self.R + 1):
            for j, (xc, yc) in enumerate(cols[c]):
                for child in (cols[c - 1][2 * j], cols[c - 1][2 * j + 1]):
                    x0, y0 = child[0] + bw / 2, child[1]
                    x1, y1 = xc - bw / 2, yc
                    midx = (x0 + x1) / 2
                    pygame.draw.line(surface, comic.INK, (x0, y0), (midx, y0), 2)
                    pygame.draw.line(surface, comic.INK, (midx, y0), (midx, y1), 2)
                    pygame.draw.line(surface, comic.INK, (midx, y1), (x1, y1), 2)

        # cajas
        for c in range(self.R + 1):
            for j, (xc, yc) in enumerate(cols[c]):
                label, state, score = self._box_content(c, j, matches, champion)
                self._draw_box(surface, xc, yc, bw, bh, label, state, score)

        # estado inferior
        if phase == "RUNNING":
            comic.outlined_text(surface, f"Jugando...  ({len(matches)} llaves resueltas)",
                                18, (cx, WINDOW_HEIGHT - 96), fill=comic.SUN1,
                                outline=comic.INK, ow=2, weight="bold")
        elif phase == "DONE":
            comic.outlined_text(surface, f"CAMPEON:  {champion}", 22,
                                (cx, WINDOW_HEIGHT - 98), fill=comic.GOLD,
                                outline=comic.INK, ow=2, weight="bold")
            if rpath:
                comic.outlined_text(surface, f"Reporte guardado en {rpath}", 12,
                                    (cx, WINDOW_HEIGHT - 76), fill=comic.PAPER,
                                    outline=comic.INK, ow=1, weight="regular")
        else:
            comic.outlined_text(surface, f"Error: {error}", 15, (cx, WINDOW_HEIGHT - 96),
                                fill=comic.RED, outline=comic.INK, ow=2, weight="bold")

        self.btn_back.draw(surface)

    def _box_content(self, c, j, matches, champion):
        if c == 0:
            return self.labels[j], "normal", None
        m = matches.get((c - 1, j))
        if m is None:
            return "", "empty", None
        score = f"{m['score'][0]}-{m['score'][1]}"
        is_champ = (c == self.R and champion == m["winner"])
        return m["winner"], ("champion" if is_champ else "winner"), score

    def _draw_box(self, surface, xc, yc, bw, bh, label, state, score):
        rect = pygame.Rect(0, 0, bw, bh)
        rect.center = (int(xc), int(yc))
        fill = {
            "empty":    (28, 40, 86),
            "normal":   comic.PANEL_FILL,
            "winner":   (46, 120, 74),
            "champion": comic.GOLD,
        }.get(state, comic.PANEL_FILL)
        pygame.draw.rect(surface, comic.INK, rect.move(3, 3), border_radius=7)
        pygame.draw.rect(surface, fill, rect, border_radius=7)
        pygame.draw.rect(surface, comic.INK, rect, 3, border_radius=7)
        if label:
            txt_col = comic.INK if state == "champion" else comic.PAPER
            lab = comic.make_label(self._fit(label, bw - 18), 13, fill=txt_col,
                                   outline=comic.INK, ow=1, weight="semibold")
            surface.blit(lab, lab.get_rect(center=rect.center))
        if score:
            sc = comic.make_label(score, 12, fill=comic.SUN1, outline=comic.INK,
                                  ow=1, weight="bold")
            surface.blit(sc, sc.get_rect(midright=(rect.right - 2, rect.bottom + 7)))

    def _fit(self, text, max_w):
        f = theme.font(13, "semibold")
        if f.size(text)[0] <= max_w:
            return text
        while text and f.size(text + "…")[0] > max_w:
            text = text[:-1]
        return text + "…"

    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return "MENU"
        return None
