"""
Identidad visual TCG / cómic energético de PokeFisi.

Paleta saturada + helpers de dibujo con el sello del estilo: contornos negros
gruesos, rayos de acción radiales, texto tipo sticker y botones con sombra dura.
Las pantallas usan estos helpers para un look coherente y reconocible.
"""
import math
import pygame
from gui import theme

# ── Paleta TCG / cómic ──────────────────────────────────────────────────────────
INK         = (24, 20, 34)        # "negro" de contornos (casi negro, cálido)
PAPER       = (255, 255, 255)

SKY         = (58, 132, 240)      # azul vibrante
SUN1        = (255, 226, 92)      # dorado/acento (título, estrellas) — NO el fondo
SUN2        = (255, 198, 48)

# Colores del FONDO (independientes del acento dorado del título)
RAY1        = (94, 198, 255)      # rayo claro del sunburst
RAY2        = (44, 150, 242)      # rayo alterno
SKY_DEEP    = (22, 52, 120)       # base detrás de los rayos
FIELD_BLUE  = (18, 42, 110)       # mitad inferior (zona de botones)

RED         = (235, 64, 68)
RED_HOVER   = (255, 99, 103)
BLUE        = (54, 138, 246)
BLUE_HOVER  = (96, 172, 255)
GREEN       = (46, 200, 108)
GREEN_HOVER = (84, 228, 142)
GOLD        = (255, 198, 54)
GOLD_HOVER  = (255, 218, 100)
SLATE       = (96, 104, 138)      # botón secundario
SLATE_HOVER = (126, 134, 168)


# ── Fondo de "estallido" (rayos de acción + viñeta) ─────────────────────────────
_bg_cache: dict = {}


def battle_background(surface: pygame.Surface, cx_ratio: float = 0.5,
                      cy_ratio: float = 0.24):
    """Fondo con sunburst (rayos alternos) que irradia desde (cx, cy) y se
    oscurece hacia abajo para que el contenido inferior resalte. Cacheado."""
    size = surface.get_size()
    key = (size, cx_ratio, cy_ratio)
    if key not in _bg_cache:
        w, h = size
        bg = pygame.Surface(size).convert()
        bg.fill(SKY_DEEP)
        cx, cy = int(w * cx_ratio), int(h * cy_ratio)
        R = int(math.hypot(w, h) * 1.2)
        n = 22
        for i in range(n):
            a0 = 2 * math.pi * i / n
            a1 = 2 * math.pi * (i + 1) / n
            col = RAY1 if i % 2 == 0 else RAY2
            pygame.draw.polygon(bg, col, [
                (cx, cy),
                (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                (cx + R * math.cos(a1), cy + R * math.sin(a1)),
            ])
        # Mitad inferior: azul vibrante LIMPIO (opaco) para que los botones
        # resalten. Zona de mezcla corta arriba; abajo azul sólido sin turbiedad.
        shade = pygame.Surface(size, pygame.SRCALPHA)
        for y in range(h):
            t = y / max(1, h - 1)
            a = 0 if t < 0.30 else min(255, int(255 * (t - 0.30) / 0.24))
            shade.fill((*FIELD_BLUE, a), (0, y, w, 1))
        bg.blit(shade, (0, 0))
        # Líneas de velocidad diagonales sutiles sobre el azul (energía cómic)
        speed = pygame.Surface(size, pygame.SRCALPHA)
        for i in range(-h, w, 46):
            pygame.draw.line(speed, (255, 255, 255, 12),
                             (i, h), (i + h, 0), 10)
        bg.blit(speed, (0, 0))
        _bg_cache[key] = bg
    surface.blit(_bg_cache[key], (0, 0))


# ── Texto tipo sticker (contorno grueso + sombra dura opcional) ──────────────────
def make_label(s: str, size: int, fill, outline=INK, ow: int = 3,
               weight: str = "bold") -> pygame.Surface:
    """Devuelve una superficie con el texto `s` relleno + contorno grueso."""
    f = theme.font(size, weight)
    base = f.render(s, True, fill)
    outl = f.render(s, True, outline)
    bw, bh = base.get_size()
    surf = pygame.Surface((bw + 2 * ow + 6, bh + 2 * ow + 6), pygame.SRCALPHA)
    cx, cy = surf.get_width() // 2, surf.get_height() // 2
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx * dx + dy * dy <= ow * ow:
                surf.blit(outl, outl.get_rect(center=(cx + dx, cy + dy)))
    surf.blit(base, base.get_rect(center=(cx, cy)))
    return surf


def outlined_text(surface, s, size, center, fill, outline=INK, ow=3,
                  weight="bold", shadow=None, rotate=0):
    """Dibuja texto sticker centrado en `center`. `shadow` = color de sombra dura."""
    if shadow is not None:
        sh = make_label(s, size, shadow, shadow, ow, weight)
        if rotate:
            sh = pygame.transform.rotate(sh, rotate)
        surface.blit(sh, sh.get_rect(center=(center[0] + 4, center[1] + 6)))
    lab = make_label(s, size, fill, outline, ow, weight)
    if rotate:
        lab = pygame.transform.rotate(lab, rotate)
    rect = lab.get_rect(center=center)
    surface.blit(lab, rect)
    return rect


# ── Formas de cómic ─────────────────────────────────────────────────────────────
def star_burst(surface, cx, cy, r_out, r_in, points, fill, outline=INK, ow=4):
    """Estrella/estallido de N puntas, relleno + contorno grueso."""
    pts = []
    for i in range(points * 2):
        ang = math.pi / points * i - math.pi / 2
        rr = r_out if i % 2 == 0 else r_in
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    pygame.draw.polygon(surface, fill, pts)
    pygame.draw.polygon(surface, outline, pts, ow)


def pokeball(surface, cx, cy, r, ow: int = 5):
    """Pokébola estilo cómic: contorno negro grueso."""
    pygame.draw.circle(surface, PAPER, (cx, cy), r)
    prev = surface.get_clip()
    surface.set_clip(pygame.Rect(cx - r, cy - r, 2 * r, r))
    pygame.draw.circle(surface, RED, (cx, cy), r)
    surface.set_clip(prev)
    pygame.draw.rect(surface, INK, (cx - r, cy - r * 0.18, 2 * r, r * 0.36))
    pygame.draw.circle(surface, INK, (cx, cy), r, ow)
    pygame.draw.circle(surface, INK, (cx, cy), int(r * 0.34))
    pygame.draw.circle(surface, PAPER, (cx, cy), int(r * 0.22))
    pygame.draw.circle(surface, INK, (cx, cy), int(r * 0.22), 3)


def ribbon(surface, center, text_str, size=18, fill=RED, text_col=PAPER,
           pad_x=22, pad_y=8, weight="semibold"):
    """Banda/etiqueta cómic (rectángulo con contorno negro) con texto centrado."""
    f = theme.font(size, weight)
    tw, th = f.size(text_str)
    w, h = tw + 2 * pad_x, th + 2 * pad_y
    rect = pygame.Rect(0, 0, w, h)
    rect.center = center
    pygame.draw.rect(surface, INK, rect.move(4, 4), border_radius=8)
    pygame.draw.rect(surface, fill, rect, border_radius=8)
    pygame.draw.rect(surface, INK, rect, 3, border_radius=8)
    outlined_text(surface, text_str, size, rect.center, fill=text_col,
                  outline=INK, ow=1, weight=weight)
    return rect
