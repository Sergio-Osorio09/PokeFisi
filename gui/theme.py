"""
Tema visual de PokeFisi — estilo moderno y limpio.

Centraliza la paleta de colores, la tipografía (Poppins) y helpers de dibujo
(degradados, paneles redondeados con sombra suave). Las pantallas deben usar
estos helpers para mantener un aspecto coherente.
"""
import os
import pygame

# ── Paleta (tema oscuro sobrio) ─────────────────────────────────────────────────
BG_TOP        = (16, 18, 30)      # degradado de fondo: arriba
BG_BOTTOM     = (28, 32, 50)      # degradado de fondo: abajo
SURFACE       = (32, 36, 56)      # paneles/tarjetas
SURFACE_LIGHT = (42, 47, 72)      # tarjetas resaltadas / hover
BORDER        = (60, 66, 96)      # bordes sutiles
SHADOW        = (0, 0, 0)         # sombra (con alpha)

TEXT          = (238, 241, 248)   # texto principal
TEXT_MUTED    = (150, 158, 178)   # texto secundario
TEXT_DIM      = (104, 112, 134)   # texto terciario

PRIMARY       = (91, 141, 239)    # acento principal (azul/indigo)
PRIMARY_HOVER = (120, 165, 250)
SUCCESS       = (46, 196, 132)    # verde (jugar)
SUCCESS_HOVER = (74, 214, 156)
DANGER        = (232, 90, 98)     # rojo (salir/eliminar)
DANGER_HOVER  = (245, 118, 125)
ACCENT        = (245, 199, 90)    # dorado (títulos/realces)

_FONT_FILES = {
    "regular":  "Poppins-Regular.ttf",
    "medium":   "Poppins-Medium.ttf",
    "semibold": "Poppins-SemiBold.ttf",
    "bold":     "Poppins-Bold.ttf",
}
_FONT_DIR = os.path.join("assets", "fonts")
_cache: dict = {}


def font(size: int, weight: str = "medium") -> pygame.font.Font:
    """Fuente Poppins en el peso pedido; cae a una sans del sistema si falta."""
    key = f"{weight}_{size}"
    if key not in _cache:
        path = os.path.join(_FONT_DIR, _FONT_FILES.get(weight, _FONT_FILES["medium"]))
        if os.path.exists(path):
            _cache[key] = pygame.font.Font(path, size)
        else:
            bold = weight in ("bold", "semibold")
            try:
                _cache[key] = pygame.font.SysFont("segoeui,arial", size, bold=bold)
            except Exception:
                _cache[key] = pygame.font.SysFont(None, size, bold=bold)
    return _cache[key]


# ── Helpers de dibujo ───────────────────────────────────────────────────────────

_grad_cache: dict = {}


def background(surface: pygame.Surface):
    """Fondo con degradado vertical (cacheado por tamaño)."""
    size = surface.get_size()
    key = (size, BG_TOP, BG_BOTTOM)
    if key not in _grad_cache:
        w, h = size
        grad = pygame.Surface(size)
        for y in range(h):
            t = y / max(1, h - 1)
            grad.fill(
                (int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t),
                 int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t),
                 int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)),
                (0, y, w, 1))
        _grad_cache[key] = grad.convert()
    surface.blit(_grad_cache[key], (0, 0))


def panel(surface: pygame.Surface, rect, radius: int = 16,
          fill=SURFACE, border=BORDER, border_w: int = 1,
          shadow: bool = True, shadow_offset: int = 6, shadow_alpha: int = 80):
    """Panel/tarjeta con esquinas redondeadas y sombra suave."""
    rect = pygame.Rect(rect)
    if shadow:
        sh = pygame.Surface((rect.w + 24, rect.h + 24), pygame.SRCALPHA)
        pygame.draw.rect(sh, (*SHADOW, shadow_alpha),
                         (12, 12, rect.w, rect.h), border_radius=radius)
        # difuminado barato: dos capas mas tenues alrededor
        pygame.draw.rect(sh, (*SHADOW, shadow_alpha // 2),
                         (10, 10, rect.w + 4, rect.h + 4), border_radius=radius + 2)
        surface.blit(sh, (rect.x - 12, rect.y - 12 + shadow_offset))
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if border_w:
        pygame.draw.rect(surface, border, rect, border_w, border_radius=radius)


def vgradient_rect(surface: pygame.Surface, rect, top, bottom, radius: int = 0):
    """Rectángulo (opcionalmente redondeado) con degradado vertical."""
    rect = pygame.Rect(rect)
    grad = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        c = (int(top[0] + (bottom[0] - top[0]) * t),
             int(top[1] + (bottom[1] - top[1]) * t),
             int(top[2] + (bottom[2] - top[2]) * t))
        pygame.draw.line(grad, c, (0, y), (rect.w, y))
    if radius > 0:
        mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.w, rect.h), border_radius=radius)
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(grad, rect.topleft)


def text(surface, s, size, pos, color=TEXT, weight="medium", center=False, right=False):
    """Atajo para renderizar texto. pos = (x, y). Devuelve el rect."""
    surf = font(size, weight).render(s, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = pos
    elif right:
        rect.topright = pos
    else:
        rect.topleft = pos
    surface.blit(surf, rect)
    return rect


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))
