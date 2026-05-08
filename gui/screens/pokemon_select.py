import random
import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT
from gui.assets_loader import get_font, get_pokemon_image, get_type_color
from gui.components.button import Button
from gui.components.pokemon_card import PokemonCard
from engine.loader import load_all_pokemon

# ── Constantes de layout ─────────────────────────────────────────────────────
COLS      = 6
CARD_W    = 152
CARD_H    = 145
PAD       = 8

HEADER_H  = 108          # alto de la cabecera (título + contador + strip)
BTN_ZONE  = 62           # alto de la zona de botones inferior
GRID_TOP  = HEADER_H     # y donde comienza la cuadrícula
GRID_BOT  = WINDOW_HEIGHT - BTN_ZONE  # y donde termina
GRID_VIS_H = GRID_BOT - GRID_TOP      # alto visible de la cuadrícula

# Anchura total de la cuadrícula
GRID_W    = COLS * CARD_W + (COLS - 1) * PAD   # 152*6 + 5*8 = 952
GRID_X    = (WINDOW_WIDTH - GRID_W - 20) // 2  # centrar dejando hueco a scrollbar

# Scrollbar
SB_X      = GRID_X + GRID_W + 6
SB_W      = 10
SB_COLOR  = (80, 80, 110)
SB_THUMB  = (160, 160, 210)


class PokemonSelect:
    def __init__(self, mode: str, team_size: int):
        self.mode       = mode
        self.team_size  = team_size
        self.all_pokemon = load_all_pokemon()

        self.font_title  = get_font(30)
        self.font_label  = get_font(17)
        self.font_small  = get_font(13)

        self.team1: list[int] = []
        self.team2: list[int] = []
        self.current_player   = 1

        # Scroll
        self.scroll_y  = 0
        rows           = (len(self.all_pokemon) + COLS - 1) // COLS
        total_h        = rows * (CARD_H + PAD) - PAD
        self.max_scroll = max(0, total_h - GRID_VIS_H)
        self._sb_dragging = False
        self._sb_drag_start = 0

        # Cartas: almacenar posición base
        self._cards: list[PokemonCard] = []
        self._base_y: list[int] = []
        self._build_cards()

        # Botones inferiores
        cx = WINDOW_WIDTH // 2
        self.btn_back  = Button((cx - 340, GRID_BOT + 8, 150, 46), "ATRAS",
                                font_size=20, color=(100,40,40), hover_color=(150,60,60))
        self.btn_start = Button((cx + 20,  GRID_BOT + 8, 150, 46), "INICIAR BATALLA",
                                font_size=17, color=(40,100,40), hover_color=(60,150,60))
        self.btn_start.enabled = False

        # Botón aleatorio (solo visible en ai_vs_ai)
        self.btn_random = Button((cx - 170, GRID_BOT + 8, 340, 46), "EQUIPOS ALEATORIOS",
                                 font_size=20, color=(60, 80, 140), hover_color=(80, 110, 190))

    def _build_cards(self):
        self._cards.clear()
        self._base_y.clear()
        for i, p in enumerate(self.all_pokemon):
            col = i % COLS
            row = i // COLS
            x   = GRID_X + col * (CARD_W + PAD)
            by  = GRID_TOP + row * (CARD_H + PAD)
            card = PokemonCard(x, by, CARD_W, CARD_H)
            card.set_pokemon(p)
            self._cards.append(card)
            self._base_y.append(by)

    def _sync_card_rects(self):
        """Actualiza card.rect.y con el desplazamiento de scroll actual."""
        for card, by in zip(self._cards, self._base_y):
            card.rect.y = by - self.scroll_y

    def _current_team(self) -> list[int]:
        return self.team1 if self.current_player == 1 else self.team2

    # ── Dibujo ───────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        surface.fill(BG_COLOR)

        self._draw_header(surface)
        self._draw_grid(surface)
        self._draw_scrollbar(surface)

        # Separador
        pygame.draw.line(surface, (70, 70, 100),
                         (0, GRID_BOT), (WINDOW_WIDTH, GRID_BOT), 1)

        self.btn_back.draw(surface)
        if self.mode == "ai_vs_ai":
            self.btn_random.draw(surface)
        else:
            self.btn_start.draw(surface)

    def _draw_header(self, surface: pygame.Surface):
        # Título
        title = self.font_title.render(self._title(), True, (255, 220, 0))
        surface.blit(title, title.get_rect(centerx=WINDOW_WIDTH // 2, top=8))

        # Contador
        count = len(self._current_team())
        info = self.font_label.render(
            f"Seleccionados: {count} / {self.team_size}", True, WHITE)
        surface.blit(info, info.get_rect(centerx=WINDOW_WIDTH // 2, top=46))

        # Franja de slots del equipo
        self._draw_team_strip(surface)

    def _draw_team_strip(self, surface: pygame.Surface):
        team   = self._current_team()
        by_id  = {p["id"]: p for p in self.all_pokemon}
        slot_w = 148
        gap    = 8
        total  = self.team_size * slot_w + (self.team_size - 1) * gap
        sx0    = (WINDOW_WIDTH - total) // 2
        sy     = 70

        for i in range(self.team_size):
            sx = sx0 + i * (slot_w + gap)
            bg = (50, 80, 50) if i < len(team) else (40, 40, 60)
            pygame.draw.rect(surface, bg, (sx, sy, slot_w, 30), border_radius=5)
            pygame.draw.rect(surface, (100, 100, 140), (sx, sy, slot_w, 30), 1, border_radius=5)

            if i < len(team):
                p   = by_id[team[i]]
                img = get_pokemon_image(p["image"], (24, 24))
                surface.blit(img, (sx + 4, sy + 3))
                name = self.font_small.render(p["name"], True, WHITE)
                surface.blit(name, (sx + 32, sy + 8))
            else:
                lbl = self.font_small.render(f"Slot {i+1}", True, (100, 100, 110))
                surface.blit(lbl, lbl.get_rect(centerx=sx + slot_w // 2, centery=sy + 15))

    def _draw_grid(self, surface: pygame.Surface):
        self._sync_card_rects()
        clip = pygame.Rect(0, GRID_TOP, WINDOW_WIDTH, GRID_VIS_H)
        surface.set_clip(clip)

        team = self._current_team()
        for i, card in enumerate(self._cards):
            # Omitir tarjetas fuera del área visible
            if card.rect.bottom < GRID_TOP or card.rect.top > GRID_BOT:
                continue
            card.selected = self.all_pokemon[i]["id"] in team
            card.draw(surface)

        surface.set_clip(None)

    def _draw_scrollbar(self, surface: pygame.Surface):
        # Track
        track = pygame.Rect(SB_X, GRID_TOP, SB_W, GRID_VIS_H)
        pygame.draw.rect(surface, SB_COLOR, track, border_radius=5)

        if self.max_scroll > 0:
            rows       = (len(self.all_pokemon) + COLS - 1) // COLS
            total_h    = rows * (CARD_H + PAD) - PAD
            ratio      = GRID_VIS_H / total_h
            thumb_h    = max(30, int(GRID_VIS_H * ratio))
            thumb_y    = GRID_TOP + int((GRID_VIS_H - thumb_h) * self.scroll_y / self.max_scroll)
            thumb      = pygame.Rect(SB_X, thumb_y, SB_W, thumb_h)
            pygame.draw.rect(surface, SB_THUMB, thumb, border_radius=5)

    # ── Eventos ──────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        # Scroll con rueda del ratón
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 35))
            return None

        # Arrastre de scrollbar
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if SB_X <= event.pos[0] <= SB_X + SB_W + 4 and GRID_TOP <= event.pos[1] <= GRID_BOT:
                self._sb_dragging   = True
                self._sb_drag_start = event.pos[1]
                return None

        if event.type == pygame.MOUSEMOTION and self._sb_dragging:
            delta = event.pos[1] - self._sb_drag_start
            self._sb_drag_start = event.pos[1]
            rows    = (len(self.all_pokemon) + COLS - 1) // COLS
            total_h = rows * (CARD_H + PAD) - PAD
            self.scroll_y = max(0, min(self.max_scroll,
                                       self.scroll_y + int(delta * total_h / GRID_VIS_H)))
            return None

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._sb_dragging = False

        # Botones de navegación
        if self.btn_back.handle_event(event):
            return "MODE_SELECT"
        if self.mode == "ai_vs_ai":
            if self.btn_random.handle_event(event):
                return self._random_battle()
        else:
            if self.btn_start.handle_event(event):
                return ("BATTLE", self.team1[:], self.team2[:])

        # Clic en tarjetas (solo si están en el área visible y no se estaba arrastrando)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if GRID_TOP <= my <= GRID_BOT:
                self._sync_card_rects()
                for i, card in enumerate(self._cards):
                    if card.rect.collidepoint(mx, my):
                        self._toggle(self.all_pokemon[i]["id"])
                        break

        return None

    # ── Lógica de selección ──────────────────────────────────────────────────
    def _toggle(self, pid: int):
        team = self._current_team()

        if pid in team:
            team.remove(pid)
        elif len(team) < self.team_size:
            team.append(pid)

        # Al completar equipo 1 → pasar a equipo 2
        if self.current_player == 1 and len(self.team1) == self.team_size:
            if len(self.team2) < self.team_size:
                self.current_player = 2
                self.scroll_y = 0

        # Si se deshace equipo 1 mientras se elige equipo 2 → volver a equipo 1
        if self.current_player == 2 and len(self.team1) < self.team_size:
            self.current_player = 1
            self.team2.clear()

        self.btn_start.enabled = (
            len(self.team1) == self.team_size and
            len(self.team2) == self.team_size
        )

    def _title(self) -> str:
        if self.mode == "human_vs_ai":
            return "Elige tu equipo" if self.current_player == 1 else "Elige el equipo de la IA rival"
        return f"Equipo IA {self.current_player}  —  o usa EQUIPOS ALEATORIOS"

    def _random_battle(self):
        all_ids = [p["id"] for p in self.all_pokemon]
        ids1 = random.sample(all_ids, self.team_size)
        ids2 = random.sample(all_ids, self.team_size)
        return ("BATTLE", ids1, ids2)
