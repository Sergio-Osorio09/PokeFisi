import random
import pygame
from config import WHITE, BG_COLOR, WINDOW_WIDTH, WINDOW_HEIGHT, AI_TURN_DELAY
from gui.assets_loader import get_font, get_pokemon_image, get_type_color
from gui.components.battle_log import BattleLog
from engine.state import BattleState
from engine.battle import Battle

# ── Layout ────────────────────────────────────────────────────────────────────
FIELD_H = 455

# Enemigo (P2) — arriba derecha
P2_SPR_X, P2_SPR_Y  = 615,  65
P2_SPR_W, P2_SPR_H  = 132, 132
P2_INFO_X, P2_INFO_Y = 475,  22

# Jugador (P1) — abajo izquierda  (sprite bajado para que la info quepa sin solaparse)
P1_SPR_X, P1_SPR_Y  = 55, 305
P1_SPR_W, P1_SPR_H  = 148, 148
P1_INFO_X, P1_INFO_Y = 55, 160

# Panel de acción — columna central vacía del campo
ACT_X = 238   # a la derecha del sprite P1 (termina en x≈203)
ACT_Y = 200   # por debajo del sprite P2 (termina en y≈197)
ACT_W = 230
ACT_H = 86

# Panel inferior
PANEL_Y = FIELD_H + 2
LOG_X, LOG_Y = 10, PANEL_Y + 6
LOG_W = 535
LOG_H = WINDOW_HEIGHT - LOG_Y - 6

BTN_X   = 553
BTN_W   = WINDOW_WIDTH - BTN_X - 10
BTN_H   = 50
BTN_GAP = 6

# Colores
HP_GREEN  = ( 80, 210,  80)
HP_YELLOW = (230, 200,  30)
HP_RED    = (220,  50,  50)
HP_BG     = ( 40,  40,  55)
GOLD      = (255, 210,   0)
NOTIFY_DUR = 2200   # ms que dura la notificación de cambio

# Indicador de equipo (miniaturas / pokébolas)
SLOT_W  = 30
SLOT_H  = 30
SLOT_GAP = 4


# ── Botones ───────────────────────────────────────────────────────────────────
class MoveButton:
    def __init__(self, index: int, move):
        self.index = index
        self.move  = move
        self.rect  = pygame.Rect(BTN_X, PANEL_Y + 6 + index * (BTN_H + BTN_GAP), BTN_W, BTN_H)
        self._hov  = False
        self.fn    = get_font(17)
        self.fs    = get_font(13)

    def draw(self, surface):
        base  = get_type_color(self.move.type)
        dark  = tuple(max(0, c - 60) for c in base)
        light = tuple(min(255, c + 25) for c in base)
        pygame.draw.rect(surface, light if self._hov else dark, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        badge_w = 55
        badge = pygame.Rect(self.rect.right - badge_w - 6, self.rect.y + 6, badge_w, 16)
        pygame.draw.rect(surface, tuple(min(255, c + 40) for c in base), badge)
        bt = get_font(11).render(self.move.type, True, WHITE)
        surface.blit(bt, bt.get_rect(center=badge.center))
        surface.blit(self.fn.render(self.move.name, True, WHITE), (self.rect.x + 8, self.rect.y + 6))
        surface.blit(self.fs.render(f"BP {self.move.base_power}   Acc {self.move.accuracy}%",
                     True, (200, 200, 180)), (self.rect.x + 8, self.rect.y + 28))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hov = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class SwitchButton:
    def __init__(self, move_count: int):
        self.rect = pygame.Rect(BTN_X, PANEL_Y + 6 + move_count * (BTN_H + BTN_GAP), BTN_W, BTN_H)
        self._hov = False
        self.font = get_font(17)

    def draw(self, surface):
        pygame.draw.rect(surface, (90, 65, 145) if self._hov else (55, 40, 105), self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        surface.blit(self.font.render("CAMBIAR POKEMON", True, WHITE),
                     self.font.render("CAMBIAR POKEMON", True, WHITE).get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._hov = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# ── Pantalla ──────────────────────────────────────────────────────────────────
class BattleScreen:
    def __init__(self, state: BattleState, agent1, agent2, mode: str,
                 label1: str = "Jugador", label2: str = "Jugador 2"):
        self.state  = state
        self.agent1 = agent1
        self.agent2 = agent2
        self.mode   = mode
        self.label1 = label1
        self.label2 = label2
        self.battle = Battle(state, agent1, agent2)

        self.fn_name  = get_font(22)
        self.fn_label = get_font(12)
        self.fn_hp    = get_font(12)
        self.fn_notify = get_font(19)

        self.log_box = BattleLog(LOG_X, LOG_Y, LOG_W, LOG_H, max_lines=13)

        self.move_buttons: list[MoveButton] = []
        self.switch_btn: SwitchButton | None = None
        self._build_buttons()

        self.finished  = False
        self.winner    = None
        self._ai_timer = 0

        # Notificación de cambio de Pokémon (panel central)
        self._notify_pokemon = None
        self._notify_player  = 0
        self._notify_timer   = 0

        # Último ataque/acción de cada jugador (texto en info panel)
        self._last_move_p1: str = ""
        self._last_move_p2: str = ""

        # Selector de cambio de Pokémon (modo humano)
        self._picking_switch  = False
        self._switch_options: list[tuple[int, object]] = []   # [(team_idx, pokemon)]

        # Tracking de Pokémon que ya han sido enviados al campo (por índice)
        self._seen_p1: set[int] = {self.state.active_index_p1}
        self._seen_p2: set[int] = {self.state.active_index_p2}

    def _build_buttons(self):
        self.move_buttons.clear()
        moves = self.state.active_pokemon_p1.get_available_moves()
        for i, mv in enumerate(moves):
            self.move_buttons.append(MoveButton(i, mv))
        self.switch_btn = SwitchButton(len(moves))

    # ── update ────────────────────────────────────────────────────────────────
    def update(self, dt: int):
        if self._notify_timer > 0:
            self._notify_timer = max(0, self._notify_timer - dt)

        if self.finished or self.state.is_terminal():
            self.finished = True
            self.winner   = self.state.get_winner()
            return

        if self.mode == "ai_vs_ai":
            self._ai_timer += dt
            if self._ai_timer >= AI_TURN_DELAY:
                self._ai_timer = 0
                prev_p1 = self.state.active_index_p1
                prev_p2 = self.state.active_index_p2

                new_lines = self.battle.step()
                for line in new_lines:
                    self.log_box.add(line)

                # Parsear acciones del turno para el panel de acción
                self._parse_actions(new_lines)

                new_p1 = self.state.active_index_p1
                new_p2 = self.state.active_index_p2
                self._seen_p1.add(new_p1)
                self._seen_p2.add(new_p2)

                # Notificación de cambio en panel central
                if new_p1 != prev_p1:
                    self._notify_pokemon = self.state.active_pokemon_p1
                    self._notify_player  = 1
                    self._notify_timer   = NOTIFY_DUR
                elif new_p2 != prev_p2:
                    self._notify_pokemon = self.state.active_pokemon_p2
                    self._notify_player  = 2
                    self._notify_timer   = NOTIFY_DUR

                if self.state.is_terminal():
                    self.finished = True
                    self.winner   = self.state.get_winner()

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        surface.fill(BG_COLOR)
        pygame.draw.line(surface, (60, 60, 90), (0, FIELD_H), (WINDOW_WIDTH, FIELD_H), 2)
        surface.fill((12, 12, 25), (0, FIELD_H + 2, WINDOW_WIDTH, WINDOW_HEIGHT - FIELD_H - 2))

        p2 = self.state.active_pokemon_p2
        p1 = self.state.active_pokemon_p1

        # Sprites — P2 de frente, P1 de espaldas (vista clásica Pokémon)
        surface.blit(get_pokemon_image(p2.image,      (P2_SPR_W, P2_SPR_H)), (P2_SPR_X, P2_SPR_Y))
        surface.blit(get_pokemon_image(p1.image_back, (P1_SPR_W, P1_SPR_H)), (P1_SPR_X, P1_SPR_Y))

        # Info flotante
        self._draw_info(surface, p2, self.label2, self.state.player2_team, self._seen_p2,
                        P2_INFO_X, P2_INFO_Y, bar_w=210, last_move=self._last_move_p2)
        self._draw_info(surface, p1, self.label1, self.state.player1_team, self._seen_p1,
                        P1_INFO_X, P1_INFO_Y, bar_w=210, last_move=self._last_move_p1)

        # Notificación de cambio
        if self._notify_timer > 0 and self._notify_pokemon:
            self._draw_switch_notify(surface)

        # Panel inferior
        self.log_box.draw(surface)
        if self.mode == "human_vs_ai" and not self.finished:
            for btn in self.move_buttons:
                btn.draw(surface)
            self.switch_btn.draw(surface)

        if self.finished:
            self._draw_winner(surface)

        if self._picking_switch:
            self._draw_switch_picker(surface)

    # ── Info flotante ─────────────────────────────────────────────────────────
    def _draw_info(self, surface, pokemon, label, team, seen_indices, x, y, bar_w, last_move=""):
        # Nombre del agente
        surface.blit(self.fn_label.render(label, True, (160, 180, 220)), (x, y))

        # Nombre Pokémon
        surface.blit(self.fn_name.render(pokemon.name, True, WHITE), (x, y + 14))

        # Último ataque / acción
        if last_move:
            col = (120, 220, 255) if last_move.startswith("↩") else (220, 220, 160)
            surface.blit(self.fn_hp.render(last_move, True, col), (x, y + 38))

        # Barra de HP  (desplazada 16px hacia abajo para dejar espacio a la acción)
        bar_x, bar_y, bar_h = x, y + 56, 10
        ratio = pokemon.current_hp / pokemon.max_hp if pokemon.max_hp > 0 else 0
        pygame.draw.rect(surface, HP_BG, (bar_x, bar_y, bar_w, bar_h))
        if ratio > 0:
            col = HP_GREEN if ratio > 0.5 else (HP_YELLOW if ratio > 0.25 else HP_RED)
            pygame.draw.rect(surface, col, (bar_x, bar_y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, (80, 80, 110), (bar_x, bar_y, bar_w, bar_h), 1)

        # HP numérico
        surface.blit(self.fn_hp.render(f"{pokemon.current_hp}/{pokemon.max_hp}",
                     True, (200, 200, 200)), (bar_x, bar_y + bar_h + 3))

        # Miniaturas / pokébolas del equipo
        self._draw_team_slots(surface, team, seen_indices, x, bar_y + bar_h + 20)

    # ── Slots del equipo: miniatura o pokébola según estado ──────────────────
    def _draw_team_slots(self, surface, team, seen_indices, x, y):
        for i, p in enumerate(team):
            sx = x + i * (SLOT_W + SLOT_GAP)
            # Fondo de slot
            pygame.draw.rect(surface, (25, 28, 48), (sx - 1, y - 1, SLOT_W + 2, SLOT_H + 2),
                             border_radius=4)
            pygame.draw.rect(surface, (55, 60, 95), (sx - 1, y - 1, SLOT_W + 2, SLOT_H + 2),
                             1, border_radius=4)

            if i not in seen_indices:
                # Pokémon no enviado aún → pokébola
                self._draw_pokeball_slot(surface, sx, y)
            elif not p.is_alive():
                # Faintado → miniatura semi-translúcida
                img = get_pokemon_image(p.image, (SLOT_W, SLOT_H))
                ghost = img.copy()
                ghost.fill((180, 180, 180, 100), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(ghost, (sx, y))
            else:
                # Vivo y ya enviado → miniatura completa
                surface.blit(get_pokemon_image(p.image, (SLOT_W, SLOT_H)), (sx, y))

    def _draw_pokeball_slot(self, surface, sx, sy):
        r  = SLOT_W // 2 - 2
        cx = sx + SLOT_W // 2
        cy = sy + SLOT_H // 2
        mid = (20, 20, 30)
        pygame.draw.circle(surface, (200, 50, 50), (cx, cy), r)
        pygame.draw.rect(surface, (220, 220, 220), (cx - r, cy, r * 2 + 1, r))
        pygame.draw.line(surface, mid, (cx - r, cy), (cx + r, cy), 2)
        pygame.draw.circle(surface, (240, 240, 240), (cx, cy), 3)
        pygame.draw.circle(surface, mid, (cx, cy), 3, 1)
        pygame.draw.circle(surface, mid, (cx, cy), r, 1)

    # ── Parseo de acciones del log ────────────────────────────────────────────
    def _parse_actions(self, lines: list[str]):
        for line in lines:
            s = line.strip()
            if " usó " in s:
                # "P1 Dragonite usó Hyper Beam! (...)"  o  "usó ...... ¡Falló!"
                try:
                    pid = s[1]   # "1" o "2"
                    move = s.split(" usó ")[1].split("!")[0].split("...")[0].strip()
                    if pid == "1":
                        self._last_move_p1 = f"→ {move}"
                    elif pid == "2":
                        self._last_move_p2 = f"→ {move}"
                except (IndexError, ValueError):
                    pass
            elif " cambia a " in s or " envía a " in s:
                try:
                    pid = s[1]
                    pname = s.split(" a ")[1].rstrip("!")
                    if pid == "1":
                        self._last_move_p1 = f"↩ {pname}"
                    elif pid == "2":
                        self._last_move_p2 = f"↩ {pname}"
                except (IndexError, ValueError):
                    pass

    # ── Notificación de cambio (columna central, sin tapar sprites) ───────────
    def _draw_switch_notify(self, surface):
        pokemon = self._notify_pokemon
        player  = self._notify_player
        pw, ph  = ACT_W, ACT_H

        # Posición: columna central del campo  (x=238, y=200)
        px, py = ACT_X, ACT_Y

        alpha = min(255, int(255 * self._notify_timer / NOTIFY_DUR * 2))

        overlay = pygame.Surface((pw, ph), pygame.SRCALPHA)
        overlay.fill((18, 20, 45, min(210, alpha)))
        surface.blit(overlay, (px, py))
        pygame.draw.rect(surface, GOLD, (px, py, pw, ph), 2)

        img = get_pokemon_image(pokemon.image, (64, 64))
        surface.blit(img, (px + 6, py + 11))

        lbl  = get_font(12).render(f"¡Jugador {player} envía a:", True, (180, 200, 230))
        name = self.fn_notify.render(pokemon.name, True, WHITE)
        surface.blit(lbl,  (px + 78, py + 20))
        surface.blit(name, (px + 78, py + 38))

    # ── Ganador ───────────────────────────────────────────────────────────────
    def _draw_winner(self, surface: pygame.Surface):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        bw, bh = 520, 150
        bx = (WINDOW_WIDTH - bw) // 2
        by = FIELD_H + (WINDOW_HEIGHT - FIELD_H - bh) // 2  # centrado en el panel inferior

        pygame.draw.rect(surface, (14, 16, 36), (bx, by, bw, bh))
        pygame.draw.rect(surface, GOLD,          (bx, by, bw, bh), 3)
        pygame.draw.rect(surface, (60, 65, 100), (bx + 5, by + 5, bw - 10, bh - 10), 1)

        if self.winner == 1:
            name, col = self.label1, (160, 255, 180)
        elif self.winner == 2:
            name, col = self.label2, (255, 160, 160)
        else:
            name, col = None, WHITE

        msg  = f"¡{name} gana!" if name else "¡Empate!"
        txt  = get_font(42).render(msg, True, col)
        hint = get_font(16).render("Presiona cualquier tecla para continuar", True, (170, 170, 200))
        surface.blit(txt,  txt.get_rect(center=(WINDOW_WIDTH // 2, by + 52)))
        surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, by + 110)))

    # ── Eventos ───────────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event):
        if self.finished:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return "RESULTS"
            return None

        # El picker de cambio tiene prioridad sobre los botones normales
        if self._picking_switch:
            self._handle_picker_event(event)
            return None

        if self.mode == "human_vs_ai":
            for btn in self.move_buttons:
                if btn.handle_event(event):
                    return self._execute_human_turn({"type": "move", "move_index": btn.index})
            if self.switch_btn and self.switch_btn.handle_event(event):
                self._try_switch()
        return None

    def _try_switch(self):
        alive = [(i, p) for i, p in enumerate(self.state.player1_team)
                 if p.is_alive() and i != self.state.active_index_p1]
        if alive:
            self._switch_options = alive
            self._picking_switch = True

    # ── Picker de selección de Pokémon ────────────────────────────────────────
    _PICKER_CARD_W = 124
    _PICKER_CARD_H = 158
    _PICKER_GAP    = 12

    def _picker_geometry(self) -> tuple[int, int, int, int]:
        """Retorna (px, py, total_w, total_h) del panel del picker."""
        n       = len(self._switch_options)
        cw, ch  = self._PICKER_CARD_W, self._PICKER_CARD_H
        total_w = n * cw + (n - 1) * self._PICKER_GAP + 40
        total_h = ch + 65
        px      = (WINDOW_WIDTH  - total_w) // 2
        py      = (WINDOW_HEIGHT - total_h) // 2
        return px, py, total_w, total_h

    def _draw_switch_picker(self, surface: pygame.Surface):
        px, py, total_w, total_h = self._picker_geometry()
        cw, ch = self._PICKER_CARD_W, self._PICKER_CARD_H
        mx, my = pygame.mouse.get_pos()

        # Fondo oscuro semitransparente
        dim = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 170))
        surface.blit(dim, (0, 0))

        # Panel
        pygame.draw.rect(surface, (14, 16, 36), (px, py, total_w, total_h), border_radius=10)
        pygame.draw.rect(surface, GOLD,          (px, py, total_w, total_h), 2, border_radius=10)

        # Título
        title = get_font(20).render("¿A qué Pokémon cambiar?", True, GOLD)
        surface.blit(title, title.get_rect(centerx=px + total_w // 2, top=py + 10))

        hint = get_font(11).render("ESC  o  clic fuera  para cancelar", True, (100, 100, 130))
        surface.blit(hint, hint.get_rect(centerx=px + total_w // 2, bottom=py + total_h - 6))

        # Tarjetas
        for i, (idx, p) in enumerate(self._switch_options):
            cx  = px + 20 + i * (cw + self._PICKER_GAP)
            cy  = py + 40
            hov = pygame.Rect(cx, cy, cw, ch).collidepoint(mx, my)

            bg  = (50, 60, 105) if hov else (28, 32, 58)
            pygame.draw.rect(surface, bg, (cx, cy, cw, ch), border_radius=8)
            bdr = GOLD if hov else (70, 80, 130)
            pygame.draw.rect(surface, bdr, (cx, cy, cw, ch), 2, border_radius=8)

            # Sprite
            img = get_pokemon_image(p.image, (72, 72))
            surface.blit(img, (cx + (cw - 72) // 2, cy + 8))

            # Nombre
            name_surf = get_font(14).render(p.name, True, WHITE)
            surface.blit(name_surf, name_surf.get_rect(centerx=cx + cw // 2, top=cy + 84))

            # Tipos
            types_txt = " / ".join(p.types) if hasattr(p, "types") else ""
            if types_txt:
                t_surf = get_font(11).render(types_txt, True, (160, 180, 220))
                surface.blit(t_surf, t_surf.get_rect(centerx=cx + cw // 2, top=cy + 100))

            # HP bar
            bw_inner = cw - 20
            ratio    = p.current_hp / p.max_hp if p.max_hp > 0 else 0
            by_bar   = cy + 116
            pygame.draw.rect(surface, HP_BG, (cx + 10, by_bar, bw_inner, 8))
            if ratio > 0:
                col = HP_GREEN if ratio > 0.5 else (HP_YELLOW if ratio > 0.25 else HP_RED)
                pygame.draw.rect(surface, col, (cx + 10, by_bar, int(bw_inner * ratio), 8))
            pygame.draw.rect(surface, (80, 80, 110), (cx + 10, by_bar, bw_inner, 8), 1)

            # HP texto
            hp_surf = get_font(11).render(f"{p.current_hp}/{p.max_hp}", True, (190, 190, 190))
            surface.blit(hp_surf, hp_surf.get_rect(centerx=cx + cw // 2, top=by_bar + 11))

    def _handle_picker_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._picking_switch = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my  = event.pos
            px, py, total_w, total_h = self._picker_geometry()
            cw, ch  = self._PICKER_CARD_W, self._PICKER_CARD_H

            # Verificar clic en cada tarjeta
            for i, (idx, _) in enumerate(self._switch_options):
                cx = px + 20 + i * (cw + self._PICKER_GAP)
                cy = py + 40
                if pygame.Rect(cx, cy, cw, ch).collidepoint(mx, my):
                    self._picking_switch = False
                    self._execute_human_turn({"type": "switch", "pokemon_index": idx})
                    return

            # Clic fuera del panel → cancelar
            if not pygame.Rect(px, py, total_w, total_h).collidepoint(mx, my):
                self._picking_switch = False

    def _execute_human_turn(self, action1: dict):
        action2 = self.agent2.choose_action(self.state, 2)
        p1 = self.state.active_pokemon_p1
        p2 = self.state.active_pokemon_p2

        self.state.turn_number += 1
        turn_header = f"=== Turno {self.state.turn_number} ==="
        self.battle.log.append(turn_header)
        new_lines = [turn_header]

        p1_first = p1.speed > p2.speed or (p1.speed == p2.speed and random.random() < 0.5)
        if p1_first:
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

        self._parse_actions(new_lines)
        self._seen_p1.add(self.state.active_index_p1)
        self._seen_p2.add(self.state.active_index_p2)

        self._build_buttons()

        if self.state.is_terminal():
            self.finished = True
            self.winner   = self.state.get_winner()
        return None
