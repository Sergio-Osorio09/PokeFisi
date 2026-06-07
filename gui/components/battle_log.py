import pygame
from config import WHITE
from gui.assets_loader import get_font

DIALOG_BG  = (10,  13,  28)
DIALOG_BDR = (140, 155, 210)
GOLD       = (255, 210,   0)
MOVE_COL   = (210, 210, 210)
DEFEAT_COL = (255, 120, 120)
SEND_COL   = (120, 220, 255)


class BattleLog:
    def __init__(self, x: int, y: int, width: int, height: int, max_lines: int = 13):
        self.rect      = pygame.Rect(x, y, width, height)
        self.font      = get_font(13)
        self.lines:    list[str] = []
        self.max_lines = max_lines
        self._max_text_w = width - 20   # ancho disponible para el texto

    def add(self, text: str):
        self.lines.append(text)
        if len(self.lines) > self.max_lines * 6:
            self.lines = self.lines[-self.max_lines * 6:]

    # ── Envuelve una línea en fragmentos que caben en _max_text_w ─────────────
    def _wrap(self, text: str) -> list[str]:
        words   = text.split(' ')
        result  = []
        current = ''
        # Indentación: si la línea original empieza con espacios, mantenerla en continuaciones
        indent  = '  ' if text.startswith('  ') else ''

        for word in words:
            test = (current + ' ' + word).lstrip() if current else word
            if self.font.size(test)[0] <= self._max_text_w:
                current = test
            else:
                if current:
                    result.append(current)
                # Nueva línea con indentación de continuación
                current = indent + word
        if current:
            result.append(current)
        return result if result else [text]

    # ── Dibujo ────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        # Fondo
        pygame.draw.rect(surface, DIALOG_BG, self.rect)
        # Borde exterior dorado
        pygame.draw.rect(surface, GOLD,       self.rect, 3)
        # Borde interior sutil
        pygame.draw.rect(surface, DIALOG_BDR, self.rect.inflate(-8, -8), 1)

        # Expandir líneas con word wrap
        wrapped: list[tuple[str, str]] = []   # (texto_display, línea_original)
        for raw in self.lines:
            for fragment in self._wrap(raw):
                wrapped.append((fragment, raw))

        # Mostrar solo las últimas max_lines líneas expandidas
        visible  = wrapped[-self.max_lines:]
        line_h   = self.font.get_linesize() + 1
        pad_x    = self.rect.x + 10
        pad_y    = self.rect.y + 8

        for i, (text, original) in enumerate(visible):
            color = self._line_color(original)
            surf  = self.font.render(text, True, color)
            surface.blit(surf, (pad_x, pad_y + i * line_h))

        # Indicador (triángulo dibujado) si hay contenido anterior no visible
        if len(wrapped) > self.max_lines:
            ax, ay = self.rect.right - 20, self.rect.bottom - 18
            pygame.draw.polygon(surface, GOLD,
                                [(ax, ay), (ax + 11, ay), (ax + 5, ay + 7)])

    # ── Color según tipo de línea ─────────────────────────────────────────────
    def _line_color(self, line: str) -> tuple:
        if line.startswith("==="):
            return GOLD
        if "derrotado" in line:
            return DEFEAT_COL
        if "envía a" in line or "cambia a" in line:
            return SEND_COL
        if "Muy efectivo" in line:
            return (255, 220, 80)
        if "No afecta" in line:
            return (150, 150, 150)
        if "Poco efectivo" in line:
            return (180, 180, 140)
        return MOVE_COL
