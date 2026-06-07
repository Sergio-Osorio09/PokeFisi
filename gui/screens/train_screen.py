"""
Pantalla de entrenamiento del Algoritmo Genetico sobre Minimax.

El entrenamiento (run_genetic) es costoso, asi que corre en un hilo de fondo
y la pantalla refresca una barra de progreso + grafica de fitness por
generacion sin congelar la interfaz. Al terminar guarda los pesos y refresca
el registro para que el nuevo agente sea seleccionable sin reiniciar.
"""
import os
import threading

import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from gui.assets_loader import get_font
from gui.components.button import Button
from gui import comic
from ai.genetic_trainer import run_genetic, save_genetic_weights, default_opponent_panel
from ai.registry import refresh_registry
from ai.heuristic_advanced import DEFAULT_WEIGHTS

_LABELS = ["supervivencia", "hp_diff", "tipo", "velocidad"]

# Opciones configurables (valor mostrado en el selector < valor >)
_POP_OPTS    = [8, 12, 16, 20]
_GEN_OPTS    = [10, 15, 20, 30]
_BATTLE_OPTS = [10, 20, 30, 50]
_DEPTH_OPTS  = [2, 3]

# Estimacion grosera de tiempo por batalla de minimax (ms), por profundidad.
# Solo orienta al usuario; varia con la maquina.
_MS_PER_BATTLE = {2: 120, 3: 900}


class TrainScreen:
    def __init__(self):
        self.font_title = get_font(34)
        self.font_lbl   = get_font(20)
        self.font_val   = get_font(22)
        self.font_info  = get_font(15)
        self.font_big   = get_font(48)

        cx = WINDOW_WIDTH // 2

        # ── Selectores de parametros ─────────────────────────────────────────
        self._pop_i = 1     # 12
        self._gen_i = 1     # 15
        self._bat_i = 1     # 6
        self._dep_i = 0     # 2

        self._rows = [
            ("Poblacion",            "_pop_i", _POP_OPTS),
            ("Generaciones",         "_gen_i", _GEN_OPTS),
            ("Batallas/individuo",   "_bat_i", _BATTLE_OPTS),
            ("Profundidad Minimax",  "_dep_i", _DEPTH_OPTS),
        ]
        self._row_y0, self._row_step = 175, 66
        self._sel_buttons = []   # (prev_btn, next_btn, attr, opts)
        for i, (_, attr, opts) in enumerate(self._rows):
            y = self._row_y0 + i * self._row_step
            prev = Button((cx + 20,  y, 38, 38), "<", font_size=18)
            nxt  = Button((cx + 190, y, 38, 38), ">", font_size=18)
            self._sel_buttons.append((prev, nxt, attr, opts))

        # ── Navegacion ───────────────────────────────────────────────────────
        self.btn_back  = Button((cx - 250, 640, 180, 50), "ATRAS",
                                font_size=20, color=(100,40,40), hover_color=(150,60,60))
        self.btn_start = Button((cx + 70,  640, 180, 50), "ENTRENAR",
                                font_size=20, color=(40,120,60), hover_color=(60,170,90))
        self.btn_cancel = Button((cx - 90, 660, 180, 50), "CANCELAR",
                                 font_size=20, color=(120,60,40), hover_color=(170,90,60))
        self.btn_done  = Button((cx - 90,  690, 180, 50), "VOLVER",
                                font_size=20, color=(40,90,160), hover_color=(60,130,200))

        # ── Estado del entrenamiento (compartido con el hilo) ────────────────
        self._lock      = threading.Lock()
        self.phase      = "CONFIG"   # CONFIG | RUNNING | DONE | ERROR
        self._history   = []         # [(gen, best_gen, best_global, avg)]
        self._total     = 0          # generaciones objetivo
        self._cur_gen   = 0
        self._best      = 0.0        # mejor fitness global (progreso fino)
        self._frac      = 0.0        # fraccion de batallas completadas [0,1]
        self._done_b    = 0
        self._total_b   = 0
        self._cancel    = False
        self._result    = None
        self._save_path = None
        self._error     = None
        self._thread    = None

    # ── helpers de config ──────────────────────────────────────────────────

    def _cur_value(self, attr, opts):
        return opts[getattr(self, attr)]

    def _estimate(self) -> int:
        pop = _POP_OPTS[self._pop_i]
        gen = _GEN_OPTS[self._gen_i]
        bat = _BATTLE_OPTS[self._bat_i]
        return pop * gen * bat

    def _estimate_seconds(self) -> float:
        depth = _DEPTH_OPTS[self._dep_i]
        return self._estimate() * _MS_PER_BATTLE.get(depth, 1000) / 1000.0

    @staticmethod
    def _fmt_time(secs: float) -> str:
        if secs < 90:
            return f"~{secs:.0f} s"
        if secs < 3600:
            return f"~{secs/60:.0f} min"
        return f"~{secs/3600:.1f} h"

    # ── arranque del hilo ────────────────────────────────────────────────────

    def _start_training(self):
        pop   = _POP_OPTS[self._pop_i]
        gen   = _GEN_OPTS[self._gen_i]
        bat   = _BATTLE_OPTS[self._bat_i]
        depth = _DEPTH_OPTS[self._dep_i]

        with self._lock:
            self._total   = gen
            self._total_b = pop * gen * bat
            self._cur_gen = 0
            self._frac    = 0.0
            self._best    = 0.0
        self.phase = "RUNNING"
        self._thread = threading.Thread(
            target=self._worker, args=(pop, gen, bat, depth), daemon=True)
        self._thread.start()

    def _worker(self, pop, gen, bat, depth):
        try:
            data = run_genetic(
                pop_size=pop,
                generations=gen,
                battles_per_eval=bat,
                minimax_depth=depth,
                opponent_factories=default_opponent_panel(),
                callback=self._on_generation,
                progress_cb=self._on_progress,
                should_stop=lambda: self._cancel,
            )
            path = save_genetic_weights(data)
            refresh_registry()
            with self._lock:
                self._result = data
                self._save_path = path
                self.phase = "DONE"
        except Exception as exc:   # pragma: no cover - defensivo
            with self._lock:
                self._error = str(exc)
                self.phase = "ERROR"

    def _on_generation(self, gen, total, best_gen, best_global, avg, population):
        with self._lock:
            self._history.append((gen, best_gen, best_global, avg))
            self._total = total

    def _on_progress(self, done_b, total_b, gen, total_g, best_global):
        with self._lock:
            self._done_b  = done_b
            self._total_b = total_b
            self._frac    = (done_b / total_b) if total_b else 0.0
            self._cur_gen = gen
            self._total   = total_g
            self._best    = best_global

    # ── update / draw ──────────────────────────────────────────────────────

    def update(self, dt: int = 0):
        pass

    def draw(self, surface: pygame.Surface):
        comic.sub_background(surface)
        if self.phase == "CONFIG":
            self._draw_config(surface)
        elif self.phase == "RUNNING":
            self._draw_running(surface)
        elif self.phase == "DONE":
            self._draw_done(surface)
        else:
            self._draw_error(surface)

    def _draw_config(self, surface):
        cx = WINDOW_WIDTH // 2
        comic.title(surface, "Entrenar IA Genetica", (cx, 76), size=34)

        sub = self.font_info.render(
            "El AG evoluciona los pesos de un Minimax contra un panel (Random/Basica/Avanzada).",
            True, (190, 190, 210))
        surface.blit(sub, sub.get_rect(centerx=cx, top=108))
        sub2 = self.font_info.render(
            "Minimax es costoso: valores altos tardan varios minutos.",
            True, (190, 190, 210))
        surface.blit(sub2, sub2.get_rect(centerx=cx, top=130))

        for i, (label, attr, opts) in enumerate(self._rows):
            y = self._row_y0 + i * self._row_step
            lbl = self.font_lbl.render(label, True, WHITE)
            surface.blit(lbl, lbl.get_rect(right=cx - 10, centery=y + 19))

            prev, nxt, _, _ = self._sel_buttons[i]
            prev.draw(surface)
            nxt.draw(surface)
            val = self.font_val.render(str(opts[getattr(self, attr)]), True, (120, 220, 160))
            surface.blit(val, val.get_rect(centerx=cx + 124, centery=y + 19))

        est = self._estimate()
        est_surf = self.font_info.render(
            f"Total: {est} batallas de minimax   (tiempo estimado {self._fmt_time(self._estimate_seconds())})",
            True, (230, 200, 120))
        surface.blit(est_surf, est_surf.get_rect(centerx=cx, top=460))
        if _DEPTH_OPTS[self._dep_i] == 3:
            warn = self.font_info.render(
                "Profundidad 3 es MUY lenta (~8 s/batalla). Usa valores bajos para probar.",
                True, (240, 150, 120))
            surface.blit(warn, warn.get_rect(centerx=cx, top=484))

        self.btn_back.draw(surface)
        self.btn_start.draw(surface)

    def _draw_running(self, surface):
        cx = WINDOW_WIDTH // 2
        with self._lock:
            hist        = list(self._history)
            total_g     = self._total or 1
            cur_gen     = max(self._cur_gen, 1)
            best_global = self._best
            frac        = self._frac
            done_b      = self._done_b
            total_b     = self._total_b
            cancelling  = self._cancel

        avg = hist[-1][3] if hist else 0.0

        comic.title(surface, "Evolucionando...", (cx, 76), size=34)

        # Texto de progreso (generacion + batallas)
        gtxt = self.font_lbl.render(f"Generacion {cur_gen} / {total_g}", True, WHITE)
        surface.blit(gtxt, gtxt.get_rect(centerx=cx, top=118))
        btxt = self.font_info.render(f"batalla {done_b} / {total_b}", True, (180, 190, 210))
        surface.blit(btxt, btxt.get_rect(centerx=cx, top=146))

        # Barra de progreso (fraccion de batallas completadas)
        bar_w, bar_h = 600, 26
        bx, by = cx - bar_w // 2, 168
        pygame.draw.rect(surface, (45, 50, 70), (bx, by, bar_w, bar_h), border_radius=6)
        pygame.draw.rect(surface, (90, 170, 240),
                         (bx, by, int(bar_w * frac), bar_h), border_radius=6)
        pygame.draw.rect(surface, WHITE, (bx, by, bar_w, bar_h), 2, border_radius=6)
        pct = self.font_info.render(f"{frac:.0%}", True, WHITE)
        surface.blit(pct, pct.get_rect(center=(cx, by + bar_h // 2)))

        # Fitness grande
        bpe = _BATTLE_OPTS[self._bat_i]
        big = self.font_big.render(f"{best_global:.0%}", True, (120, 230, 150))
        surface.blit(big, big.get_rect(centerx=cx, top=210))
        flbl = self.font_info.render(
            f"mejor individuo (sobre {bpe} batallas, escenarios comunes)", True, (180, 200, 180))
        surface.blit(flbl, flbl.get_rect(centerx=cx, top=266))
        albl = self.font_info.render(
            f"promedio poblacion (senal real): {avg:.0%}", True, (200, 200, 150))
        surface.blit(albl, albl.get_rect(centerx=cx, top=290))

        # Grafica de evolucion (best_global verde, promedio gris)
        self._draw_chart(surface, hist, total_g, top=322, height=210)

        if cancelling:
            c = self.font_info.render("Cancelando... (se detiene tras la batalla actual)",
                                      True, (240, 180, 120))
            surface.blit(c, c.get_rect(centerx=cx, top=596))
            self.btn_done.draw(surface)   # permite volver al menu de inmediato
        else:
            self.btn_cancel.draw(surface)

    def _draw_chart(self, surface, hist, total, top, height):
        cx = WINDOW_WIDTH // 2
        chart_w = 700
        x0 = cx - chart_w // 2
        base_y = top + height

        # Marco
        pygame.draw.rect(surface, (35, 40, 60), (x0, top, chart_w, height), border_radius=6)
        pygame.draw.rect(surface, (70, 80, 110), (x0, top, chart_w, height), 1, border_radius=6)
        # Lineas guia 50% y 100%
        for frac, txt in ((1.0, "100%"), (0.5, "50%")):
            gy = base_y - int(height * frac)
            pygame.draw.line(surface, (55, 62, 88), (x0, gy), (x0 + chart_w, gy), 1)
            t = self.font_info.render(txt, True, (110, 120, 150))
            surface.blit(t, (x0 - 38, gy - 8))

        if len(hist) < 1:
            return

        n = max(len(hist), total, 2)
        def px(i): return x0 + int(chart_w * (i / (n - 1))) if n > 1 else x0
        def py(v): return base_y - int(height * max(0.0, min(1.0, v)))

        # Promedio (gris) y mejor global (verde)
        avg_pts = [(px(i), py(h[3])) for i, h in enumerate(hist)]
        glb_pts = [(px(i), py(h[2])) for i, h in enumerate(hist)]
        if len(avg_pts) > 1:
            pygame.draw.lines(surface, (140, 140, 160), False, avg_pts, 2)
        if len(glb_pts) > 1:
            pygame.draw.lines(surface, (90, 220, 130), False, glb_pts, 3)
        for p in glb_pts:
            pygame.draw.circle(surface, (130, 240, 160), p, 3)

        # Leyenda
        lx = x0 + 12
        pygame.draw.line(surface, (90, 220, 130), (lx, top + 14), (lx + 24, top + 14), 3)
        surface.blit(self.font_info.render("mejor global", True, (170, 220, 180)),
                     (lx + 32, top + 6))
        pygame.draw.line(surface, (140, 140, 160), (lx, top + 34), (lx + 24, top + 34), 2)
        surface.blit(self.font_info.render("promedio", True, (180, 180, 200)),
                     (lx + 32, top + 26))

    def _draw_done(self, surface):
        cx = WINDOW_WIDTH // 2
        with self._lock:
            data = self._result
            path = self._save_path
            hist = list(self._history)

        cancelled = self._cancel
        title_txt = "Entrenamiento cancelado" if cancelled else "Entrenamiento completado!"
        comic.title(surface, title_txt, (cx, 76), size=30)

        fit = data.get("fitness", 0.0) if data else 0.0
        big = self.font_big.render(f"{fit:.0%}", True, (120, 230, 150))
        surface.blit(big, big.get_rect(centerx=cx, top=110))
        flbl = self.font_info.render("fitness final (win-rate vs panel: Random/Basica/Avanzada)",
                                     True, (180, 200, 180))
        surface.blit(flbl, flbl.get_rect(centerx=cx, top=168))

        # Pesos evolucionados vs base
        weights = data.get("weights", []) if data else []
        head = self.font_lbl.render("Pesos evolucionados (vs base)", True, WHITE)
        surface.blit(head, head.get_rect(centerx=cx, top=205))
        for i, lbl in enumerate(_LABELS):
            y = 245 + i * 34
            wv = weights[i] if i < len(weights) else 0.0
            dv = DEFAULT_WEIGHTS[i]
            diff = wv - dv
            sign = "+" if diff >= 0 else ""
            color = (120, 220, 140) if diff >= 0 else (220, 150, 120)
            lbl_s = self.font_info.render(f"{lbl}", True, (200, 200, 210))
            surface.blit(lbl_s, lbl_s.get_rect(right=cx - 90, top=y))
            # barra proporcional
            pygame.draw.rect(surface, (50, 60, 85), (cx - 75, y + 2, 150, 12), border_radius=3)
            pygame.draw.rect(surface, color, (cx - 75, y + 2, int(150 * wv), 12), border_radius=3)
            val_s = self.font_info.render(f"{wv:.3f}  (base {dv:.2f}, {sign}{diff:.3f})",
                                          True, color)
            surface.blit(val_s, (cx + 90, y))

        if path:
            fname = os.path.basename(path)
            ps = self.font_info.render(f"Guardado en: data/{fname}", True, (200, 200, 130))
            surface.blit(ps, ps.get_rect(centerx=cx, top=400))
        note = self.font_info.render(
            "Ya aparece como 'Genetico ...' en NUEVA BATALLA.",
            True, (150, 200, 240))
        surface.blit(note, note.get_rect(centerx=cx, top=428))

        self._draw_chart(surface, hist, len(hist), top=470, height=150)
        self.btn_done.draw(surface)

    def _draw_error(self, surface):
        cx = WINDOW_WIDTH // 2
        comic.outlined_text(surface, "Error en el entrenamiento", 34, (cx, 140),
                            fill=(245, 140, 140), outline=comic.INK, ow=4,
                            weight="bold", shadow=comic.RED)
        msg = self.font_info.render(str(self._error or "desconocido"), True, (230, 200, 200))
        surface.blit(msg, msg.get_rect(centerx=cx, top=180))
        self.btn_done.draw(surface)

    # ── eventos ──────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if self.phase == "CONFIG":
            for prev, nxt, attr, opts in self._sel_buttons:
                if prev.handle_event(event):
                    setattr(self, attr, (getattr(self, attr) - 1) % len(opts))
                if nxt.handle_event(event):
                    setattr(self, attr, (getattr(self, attr) + 1) % len(opts))
            if self.btn_back.handle_event(event):
                return "MENU"
            if self.btn_start.handle_event(event):
                self._start_training()
            return None

        if self.phase == "RUNNING":
            if self._cancel:
                # Ya cancelando: permitir volver al menu sin esperar
                # (el hilo daemon termina la batalla en curso y se cierra solo).
                if self.btn_done.handle_event(event):
                    return "MENU"
            elif self.btn_cancel.handle_event(event):
                self._cancel = True
            return None

        # DONE / ERROR
        if self.btn_done.handle_event(event):
            return "MENU"
        return None
