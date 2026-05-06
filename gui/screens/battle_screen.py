import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT, AI_TURN_DELAY, GREEN, YELLOW, RED
from gui.assets_loader import get_font, get_pokemon_image, get_type_color
from gui.components.hp_bar import HPBar
from gui.components.battle_log import BattleLog
from engine.state import BattleState
from engine.battle import Battle

# ── Layout ──────────────────────────────────────────────────────────────────
FIELD_H      = 450          # altura del campo de batalla

# Enemigo (P2) — arriba izquierda
P2_SPR_X, P2_SPR_Y   = 60,  30
P2_SPR_SIZE           = (148, 148)
P2_INFO_X, P2_INFO_Y  = 230, 38   # info de texto a la derecha del sprite

# Jugador (P1) — abajo derecha
P1_SPR_X, P1_SPR_Y   = 700, 250
P1_SPR_SIZE           = (148, 148)
P1_INFO_X, P1_INFO_Y  = 40,  340  # info de texto abajo izquierda

# Panel inferior
PANEL_Y = FIELD_H + 8

# Log (izquierda del panel inferior)
LOG_X, LOG_Y = 10, PANEL_Y
LOG_W        = 520
LOG_H        = WINDOW_HEIGHT - PANEL_Y - 8

# Botones de movimiento (derecha del panel inferior)
BTN_X     = 545
BTN_W     = WINDOW_WIDTH - BTN_X - 10
BTN_H     = 48
BTN_GAP   = 6


class MoveButton:
    """Botón de movimiento que muestra nombre, tipo, BP y precisión."""
    def __init__(self, index: int, move):
        self.index = index
        self.move = move
        self.rect = pygame.Rect(
            BTN_X,
            PANEL_Y + index * (BTN_H + BTN_GAP),
            BTN_W,
            BTN_H,
        )
        self._hovered = False
        self.font_name = get_font(17)
        self.font_stat = get_font(13)

    def draw(self, surface: pygame.Surface):
        base = get_type_color(self.move.type)
        dark = tuple(max(0, c - 70) for c in base)
        color = tuple(min(255, c + 20) for c in base) if self._hovered else dark
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=6)

        # Nombre del movimiento
        name_surf = self.font_name.render(self.move.name, True, WHITE)
        surface.blit(name_surf, (self.rect.x + 10, self.rect.y + 5))

        # Estadísticas: Tipo | BP | Acc
        stats_text = f"{self.move.type}   BP: {self.move.base_power}   Acc: {self.move.accuracy}%"
        stat_surf = self.font_stat.render(stats_text, True, (220, 220, 220))
        surface.blit(stat_surf, (self.rect.x + 10, self.rect.y + 26))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class SwitchButton:
    """Botón para cambiar Pokémon."""
    def __init__(self, move_count: int):
        self.rect = pygame.Rect(
            BTN_X,
            PANEL_Y + move_count * (BTN_H + BTN_GAP),
            BTN_W,
            BTN_H,
        )
        self._hovered = False
        self.font = get_font(17)

    def draw(self, surface: pygame.Surface):
        color = (100, 80, 160) if self._hovered else (65, 50, 110)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=6)
        label = self.font.render("CAMBIAR POKEMON", True, WHITE)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class BattleScreen:
    def __init__(self, state: BattleState, agent1, agent2, mode: str):
        self.state  = state
        self.agent1 = agent1
        self.agent2 = agent2
        self.mode   = mode
        self.battle = Battle(state, agent1, agent2)

        self.font_name  = get_font(24)
        self.font_type  = get_font(15)
        self.font_small = get_font(14)

        self.hp_bar_p2 = HPBar(P2_INFO_X, P2_INFO_Y + 30, 260, 16)
        self.hp_bar_p1 = HPBar(P1_INFO_X, P1_INFO_Y + 30, 260, 16)

        self.log_box = BattleLog(LOG_X, LOG_Y, LOG_W, LOG_H, max_lines=12)

        self.move_buttons: list[MoveButton] = []
        self.switch_btn: SwitchButton | None = None
        self._build_buttons()

        self.finished = False
        self.winner   = None
        self._ai_timer = 0

    def _build_buttons(self):
        self.move_buttons.clear()
        moves = self.state.active_pokemon_p1.get_available_moves()
        for i, mv in enumerate(moves):
            self.move_buttons.append(MoveButton(i, mv))
        self.switch_btn = SwitchButton(len(moves))

    # ── update ──────────────────────────────────────────────────────────────
    def update(self, dt: int):
        if self.finished or self.state.is_terminal():
            self.finished = True
            self.winner   = self.state.get_winner()
            return

        if self.mode == "ai_vs_ai":
            self._ai_timer += dt
            if self._ai_timer >= AI_TURN_DELAY:
                self._ai_timer = 0
                new_lines = self.battle.step()
                for line in new_lines:
                    self.log_box.add(line)
                if self.state.is_terminal():
                    self.finished = True
                    self.winner   = self.state.get_winner()

    # ── draw ────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        surface.fill((30, 30, 55))

        # Línea divisora campo / panel
        pygame.draw.line(surface, (80, 80, 120),
                         (0, FIELD_H), (WINDOW_WIDTH, FIELD_H), 2)

        p1 = self.state.active_pokemon_p1
        p2 = self.state.active_pokemon_p2

        # ── Enemigo (P2) — arriba izquierda ─────────────────────────────────
        img2 = get_pokemon_image(p2.image, P2_SPR_SIZE)
        surface.blit(img2, (P2_SPR_X, P2_SPR_Y))

        # Nombre P2
        n2 = self.font_name.render(p2.name, True, WHITE)
        surface.blit(n2, (P2_INFO_X, P2_INFO_Y))
        # Tipo P2
        t2 = self.font_type.render("/".join(p2.types), True, get_type_color(p2.types[0]))
        surface.blit(t2, (P2_INFO_X, P2_INFO_Y + 50))
        # HP bar P2
        self.hp_bar_p2.draw(surface, p2.current_hp, p2.max_hp)
        hp2_txt = self.font_small.render(f"{p2.current_hp}/{p2.max_hp}", True, WHITE)
        surface.blit(hp2_txt, (P2_INFO_X + 268, P2_INFO_Y + 28))
        # Team dots P2
        self._draw_team_dots(surface, self.state.player2_team, P2_INFO_X, P2_INFO_Y + 70)

        # ── Jugador (P1) — abajo derecha ────────────────────────────────────
        img1 = get_pokemon_image(p1.image, P1_SPR_SIZE)
        surface.blit(img1, (P1_SPR_X, P1_SPR_Y))

        # Nombre P1
        n1 = self.font_name.render(p1.name, True, WHITE)
        surface.blit(n1, (P1_INFO_X, P1_INFO_Y))
        # Tipo P1
        t1 = self.font_type.render("/".join(p1.types), True, get_type_color(p1.types[0]))
        surface.blit(t1, (P1_INFO_X, P1_INFO_Y + 50))
        # HP bar P1
        self.hp_bar_p1.draw(surface, p1.current_hp, p1.max_hp)
        hp1_txt = self.font_small.render(f"{p1.current_hp}/{p1.max_hp}", True, WHITE)
        surface.blit(hp1_txt, (P1_INFO_X + 268, P1_INFO_Y + 28))
        # Team dots P1
        self._draw_team_dots(surface, self.state.player1_team, P1_INFO_X, P1_INFO_Y + 70)

        # ── Panel inferior ───────────────────────────────────────────────────
        self.log_box.draw(surface)

        if self.mode == "human_vs_ai" and not self.finished:
            for btn in self.move_buttons:
                btn.draw(surface)
            self.switch_btn.draw(surface)

        if self.finished:
            self._draw_winner(surface)

    def _draw_team_dots(self, surface, team, x, y):
        for i, p in enumerate(team):
            color = (60, 200, 60) if p.is_alive() else (180, 50, 50)
            pygame.draw.circle(surface, color, (x + i * 22, y), 8)
            pygame.draw.circle(surface, WHITE,  (x + i * 22, y), 8, 1)

    def _draw_winner(self, surface: pygame.Surface):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        font = get_font(52)
        msg = f"¡Jugador {self.winner} gana!" if self.winner else "¡Empate!"
        txt = font.render(msg, True, (255, 220, 0))
        surface.blit(txt, txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))
        hint = get_font(20).render("Presiona cualquier tecla para continuar", True, WHITE)
        surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80)))

    # ── events ──────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        if self.finished:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return "RESULTS"
            return None

        if self.mode == "human_vs_ai":
            for btn in self.move_buttons:
                if btn.handle_event(event):
                    return self._execute_human_turn({"type": "move", "move_index": btn.index})
            if self.switch_btn and self.switch_btn.handle_event(event):
                self._try_switch()
        return None

    def _try_switch(self):
        alive = [
            (i, p) for i, p in enumerate(self.state.player1_team)
            if p.is_alive() and i != self.state.active_index_p1
        ]
        if alive:
            idx, _ = alive[0]
            self._execute_human_turn({"type": "switch", "pokemon_index": idx})

    def _execute_human_turn(self, action1: dict):
        action2 = self.agent2.choose_action(self.state, 2)
        p1 = self.state.active_pokemon_p1
        p2 = self.state.active_pokemon_p2

        self.state.turn_number += 1
        turn_header = f"=== Turno {self.state.turn_number} ==="
        self.battle.log.append(turn_header)
        new_lines = [turn_header]

        if p1.speed >= p2.speed:
            new_lines += self.battle._apply_and_log_action(self.state, 1, action1)
            if not self.state.is_terminal():
                new_lines += self.battle._apply_and_log_action(self.state, 2, action2)
        else:
            new_lines += self.battle._apply_and_log_action(self.state, 2, action2)
            if not self.state.is_terminal():
                new_lines += self.battle._apply_and_log_action(self.state, 1, action1)

        self.battle._auto_replace_log(self.state, new_lines)

        for line in new_lines:
            self.log_box.add(line)

        self._build_buttons()

        if self.state.is_terminal():
            self.finished = True
            self.winner   = self.state.get_winner()

        return None
