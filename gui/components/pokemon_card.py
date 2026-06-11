import pygame
from config import WHITE, DARK, BLACK
from gui.assets_loader import get_font, get_pokemon_image, get_type_color
from engine.pokemon import battle_stats


class PokemonCard:
    def __init__(self, x: int, y: int, width: int = 130, height: int = 150):
        self.rect = pygame.Rect(x, y, width, height)
        self.font_name = get_font(14)
        self.font_type = get_font(11)
        self.font_stat = get_font(11)
        self.selected = False
        self.disabled = False
        self._hovered = False
        self._pokemon_data = None

    def set_pokemon(self, data: dict):
        self._pokemon_data = data

    def draw(self, surface: pygame.Surface):
        if not self._pokemon_data:
            return
        p = self._pokemon_data
        # Card background
        bg = (50, 50, 80) if not self.selected else (80, 120, 80)
        if self.disabled:
            bg = (40, 40, 40)
        border = (200, 200, 60) if self.selected else (100, 100, 150)
        if self._hovered and not self.disabled:
            bg = tuple(min(255, c + 30) for c in bg)

        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)

        # Sprite
        img = get_pokemon_image(p["image"], (56, 56))
        img_x = self.rect.x + (self.rect.width - 56) // 2
        surface.blit(img, (img_x, self.rect.y + 4))

        # Name
        name_surf = self.font_name.render(p["name"], True, WHITE)
        name_rect = name_surf.get_rect(centerx=self.rect.centerx, top=self.rect.y + 62)
        surface.blit(name_surf, name_rect)

        # Types
        ty = "/".join(p["types"])
        type_color = get_type_color(p["types"][0])
        ty_surf = self.font_type.render(ty, True, type_color)
        surface.blit(ty_surf, ty_surf.get_rect(centerx=self.rect.centerx, top=self.rect.y + 78))

        # Stats mini (nivel 100: los mismos valores con los que se combate)
        s = battle_stats(p["stats"])
        stats_text = f"HP:{s['hp']} A:{s['attack']} D:{s['defense']}"
        st_surf = self.font_stat.render(stats_text, True, (180, 180, 180))
        surface.blit(st_surf, st_surf.get_rect(centerx=self.rect.centerx, top=self.rect.y + 92))

        spd_text = f"SPE:{s['speed']}"
        sp_surf = self.font_stat.render(spd_text, True, (180, 180, 180))
        surface.blit(sp_surf, sp_surf.get_rect(centerx=self.rect.centerx, top=self.rect.y + 106))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if self.disabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
