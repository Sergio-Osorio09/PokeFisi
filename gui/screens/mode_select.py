import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from gui.assets_loader import get_font
from gui.components.button import Button
from gui import comic

_WEIGHT_LABELS = ["alive", "hp_mio", "hp_opp", "tipo", "vel", "vivos"]

# Centros de columna para ai_vs_ai
AI1_CX = WINDOW_WIDTH // 4       # 256
AI2_CX = 3 * WINDOW_WIDTH // 4   # 768

BTN_W, BTN_H = 36, 36
SELECTOR_Y   = 248   # y de los botones < >
INFO_Y       = 288   # y primera línea de info (descripción)
WEIGHTS_Y    = 306   # y primer peso vertical
WEIGHT_STEP  = 15    # separación entre pesos
TEAM_Y       = 412   # y "Tamaño de equipo:"
SIZE_BTN_Y   = 436
NAV_Y        = 516


class ModeSelect:
    def __init__(self):
        self.font_title  = get_font(36)
        self.font_label  = get_font(17)
        self.font_name   = get_font(16)
        self.font_info   = get_font(12)
        self.font_wt     = get_font(12)

        cx = WINDOW_WIDTH // 2

        # ── Botones de modo ──────────────────────────────────────────────────
        self.btn_human = Button((cx - 310, 110, 280, 65), "HUMANO vs IA",
                                font_size=21, color=(40,90,160), hover_color=(60,130,200))
        self.btn_ai    = Button((cx + 30,  110, 280, 65), "IA vs IA",
                                font_size=21, color=(120,40,120), hover_color=(170,60,170))

        # ── Registro de agentes ──────────────────────────────────────────────
        # Leer del módulo (no por valor) para reflejar refrescos tras entrenar.
        from ai import registry
        self.ai_options = [name for name, _ in registry.AI_REGISTRY]
        self._ai_data   = self._build_ai_data(registry.AI_REGISTRY)
        self.ai1_idx = 0
        self.ai2_idx = 0

        # ── Botones selector IA ──────────────────────────────────────────────
        self.btn_ai1_prev = Button((AI1_CX - 195, SELECTOR_Y, BTN_W, BTN_H), "<", font_size=18)
        self.btn_ai1_next = Button((AI1_CX + 159, SELECTOR_Y, BTN_W, BTN_H), ">", font_size=18)
        self.btn_ai2_prev = Button((AI2_CX - 195, SELECTOR_Y, BTN_W, BTN_H), "<", font_size=18)
        self.btn_ai2_next = Button((AI2_CX + 159, SELECTOR_Y, BTN_W, BTN_H), ">", font_size=18)

        # ── Tamaño de equipo ─────────────────────────────────────────────────
        self.team_size = 3
        self.btn_size3 = Button((cx - 110, SIZE_BTN_Y, 90, 38), "3 vs 3",
                                font_size=17, color=(50,80,50), hover_color=(70,120,70))
        self.btn_size4 = Button((cx + 20,  SIZE_BTN_Y, 90, 38), "4 vs 4",
                                font_size=17, color=(50,80,50), hover_color=(70,120,70))

        # ── Navegación ───────────────────────────────────────────────────────
        self.btn_back  = Button((cx - 160, NAV_Y, 140, 44), "ATRAS",
                                font_size=19, color=(100,40,40), hover_color=(150,60,60))
        self.btn_start = Button((cx + 20,  NAV_Y, 140, 44), "CONTINUAR",
                                font_size=19, color=(40,100,40), hover_color=(60,150,60))

        self.mode = None

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _build_ai_data(registry):
        data = []
        for name, factory in registry:
            a = factory()
            info_lines = a.get_info_lines()
            data.append({
                "name":    name,
                "desc":    info_lines[0] if info_lines else "",
                "weights": None if hasattr(a, "get_visual_stats") else getattr(a, "weights", None),
                "battles": getattr(a, "battles_trained", None),
                "wr":      getattr(a, "win_rate_training", None),
                "stats":   a.get_visual_stats() if hasattr(a, "get_visual_stats") else None,
            })
        return data

    def _draw_selector(self, surface, col_cx, header, btn_prev, btn_next,
                       agent_idx, name_color):
        d = self._ai_data[agent_idx]

        # Header
        hdr = self.font_label.render(header, True, WHITE)
        surface.blit(hdr, hdr.get_rect(centerx=col_cx, top=215))

        # Botones y nombre en la misma fila
        btn_prev.draw(surface)
        btn_next.draw(surface)
        name_surf = self.font_name.render(d["name"], True, name_color)
        surface.blit(name_surf,
                     name_surf.get_rect(centerx=col_cx,
                                        centery=SELECTOR_Y + BTN_H // 2))

        # Descripción
        desc_surf = self.font_info.render(d["desc"], True, (170, 170, 170))
        surface.blit(desc_surf, desc_surf.get_rect(centerx=col_cx, top=INFO_Y))

        # Tabla visual de capacidades (Minimax y similares)
        if d["stats"] is not None:
            BAR_BLOCKS = 4
            BLOCK_W, BLOCK_H, BLOCK_GAP = 14, 9, 3
            LBL_RIGHT = col_cx - 8     # etiqueta alineada a la derecha de este x
            BAR_X     = col_cx         # barra empieza aquí
            TXT_X     = BAR_X + BAR_BLOCKS * (BLOCK_W + BLOCK_GAP) + 6

            for i, (label, filled, total, extra_txt) in enumerate(d["stats"]):
                y = WEIGHTS_Y + i * (WEIGHT_STEP + 4)

                # Etiqueta alineada a la derecha
                lbl_surf = self.font_wt.render(f"{label}:", True, (200, 200, 200))
                surface.blit(lbl_surf, lbl_surf.get_rect(right=LBL_RIGHT, top=y))

                # Bloques de barra
                for b in range(total):
                    bx = BAR_X + b * (BLOCK_W + BLOCK_GAP)
                    color = (100, 160, 255) if b < filled else (45, 55, 80)
                    pygame.draw.rect(surface, color,
                                     pygame.Rect(bx, y + 1, BLOCK_W, BLOCK_H),
                                     border_radius=2)

                # Texto a la derecha de la barra
                if extra_txt:
                    txt_surf = self.font_wt.render(extra_txt, True, (180, 200, 255))
                    surface.blit(txt_surf, (TXT_X, y))

        # Pesos en vertical
        if d["weights"] is not None:
            w = d["weights"]

            # Título "Pesos:" + batallas si existe
            if d["battles"] is not None:
                title = f"Pesos (WR: {d['wr']:.0%}):"
            else:
                title = "Pesos:"
            title_surf = self.font_wt.render(title, True, (220, 200, 80))
            surface.blit(title_surf,
                         title_surf.get_rect(centerx=col_cx, top=WEIGHTS_Y - 1))

            # Una fila por peso: "label  0.000"
            for i, (lbl, val) in enumerate(zip(_WEIGHT_LABELS, w)):
                y = WEIGHTS_Y + 14 + i * WEIGHT_STEP
                bar_color = self._weight_color(val)

                # Etiqueta
                lbl_surf = self.font_wt.render(f"{lbl}:", True, (200, 200, 200))
                lbl_rect = lbl_surf.get_rect(right=col_cx - 4, top=y)
                surface.blit(lbl_surf, lbl_rect)

                # Barra proporcional
                bar_w = int(val * 80)
                bar_rect = pygame.Rect(col_cx, y + 2, bar_w, 10)
                pygame.draw.rect(surface, bar_color, bar_rect, border_radius=3)

                # Valor numérico
                val_surf = self.font_wt.render(f"{val:.3f}", True, bar_color)
                surface.blit(val_surf, (col_cx + 84, y))

    @staticmethod
    def _weight_color(v: float):
        if v >= 0.30:
            return (100, 220, 100)
        if v >= 0.15:
            return (220, 200, 80)
        return (160, 160, 200)

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        comic.sub_background(surface)
        cx = WINDOW_WIDTH // 2

        comic.title(surface, "Modo de Juego", (cx, 78), size=40)

        self.btn_human.draw(surface)
        self.btn_ai.draw(surface)

        if self.mode == "human_vs_ai":
            pygame.draw.rect(surface, (255,220,0), self.btn_human.rect, 3, border_radius=10)
        elif self.mode == "ai_vs_ai":
            pygame.draw.rect(surface, (255,220,0), self.btn_ai.rect, 3, border_radius=10)

        # Línea divisora entre columnas (solo ai_vs_ai)
        if self.mode == "ai_vs_ai":
            pygame.draw.line(surface, (60,60,90),
                             (cx, 205), (cx, TEAM_Y - 10), 1)

        # ── Selectores ───────────────────────────────────────────────────────
        if self.mode == "ai_vs_ai":
            self.btn_ai2_prev.rect.x = AI2_CX - 195
            self.btn_ai2_next.rect.x = AI2_CX + 159
            self._draw_selector(surface, AI1_CX, "IA Jugador 1:",
                                 self.btn_ai1_prev, self.btn_ai1_next,
                                 self.ai1_idx, (180, 220, 255))
            self._draw_selector(surface, AI2_CX, "IA Jugador 2:",
                                 self.btn_ai2_prev, self.btn_ai2_next,
                                 self.ai2_idx, (255, 200, 255))

        elif self.mode == "human_vs_ai":
            self.btn_ai2_prev.rect.x = cx - 195
            self.btn_ai2_next.rect.x = cx + 159
            self._draw_selector(surface, cx, "IA rival:",
                                 self.btn_ai2_prev, self.btn_ai2_next,
                                 self.ai2_idx, (255, 200, 100))

        # ── Tamaño de equipo ─────────────────────────────────────────────────
        size_lbl = self.font_label.render("Tamano de equipo:", True, WHITE)
        surface.blit(size_lbl, size_lbl.get_rect(centerx=cx, top=TEAM_Y))
        self.btn_size3.draw(surface)
        self.btn_size4.draw(surface)
        if self.team_size == 3:
            pygame.draw.rect(surface, (255,220,0), self.btn_size3.rect, 3, border_radius=10)
        else:
            pygame.draw.rect(surface, (255,220,0), self.btn_size4.rect, 3, border_radius=10)

        self.btn_back.draw(surface)
        self.btn_start.enabled = self.mode is not None
        self.btn_start.draw(surface)

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        n = len(self.ai_options)

        if self.btn_human.handle_event(event): self.mode = "human_vs_ai"
        if self.btn_ai.handle_event(event):    self.mode = "ai_vs_ai"

        if self.btn_ai1_prev.handle_event(event): self.ai1_idx = (self.ai1_idx - 1) % n
        if self.btn_ai1_next.handle_event(event): self.ai1_idx = (self.ai1_idx + 1) % n
        if self.btn_ai2_prev.handle_event(event): self.ai2_idx = (self.ai2_idx - 1) % n
        if self.btn_ai2_next.handle_event(event): self.ai2_idx = (self.ai2_idx + 1) % n

        if self.btn_size3.handle_event(event): self.team_size = 3
        if self.btn_size4.handle_event(event): self.team_size = 4

        if self.btn_back.handle_event(event):  return "MENU"
        if self.btn_start.handle_event(event) and self.mode:
            return ("POKEMON_SELECT", self.mode, self.team_size, self.ai1_idx, self.ai2_idx)
        return None
