import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from gui import comic
from gui.components.button import Button


class MainMenu:
    def __init__(self):
        cx = WINDOW_WIDTH // 2
        bw, bh = 360, 56
        x = cx - bw // 2
        y0, step = 352, 66
        self.btn_battle  = Button((x, y0, bw, bh), "NUEVA BATALLA",
                                  font_size=23, color=comic.GREEN, hover_color=comic.GREEN_HOVER,
                                  style="comic")
        self.btn_tourney = Button((x, y0 + step, bw, bh), "TORNEO DE IAS",
                                  font_size=22, color=comic.GOLD, hover_color=comic.GOLD_HOVER,
                                  text_color=comic.INK, style="comic")
        self.btn_train   = Button((x, y0 + 2 * step, bw, bh), "ENTRENAR IA GENÉTICA",
                                  font_size=20, color=comic.BLUE, hover_color=comic.BLUE_HOVER,
                                  style="comic")
        self.btn_delete  = Button((x, y0 + 3 * step, bw, bh), "ELIMINAR IAS ENTRENADAS",
                                  font_size=18, color=comic.SLATE, hover_color=comic.SLATE_HOVER,
                                  style="comic")
        self.btn_exit    = Button((x, y0 + 4 * step, bw, bh), "SALIR",
                                  font_size=23, color=comic.RED, hover_color=comic.RED_HOVER,
                                  style="comic")

    def update(self, dt: int = 0):
        pass

    def draw(self, surface: pygame.Surface):
        comic.battle_background(surface)
        cx = WINDOW_WIDTH // 2

        # Emblema: estallido + pokébola
        comic.star_burst(surface, cx, 132, 92, 58, 16, comic.SUN1, comic.INK, ow=4)
        comic.star_burst(surface, cx, 132, 78, 50, 16, comic.PAPER, comic.INK, ow=3)
        comic.pokeball(surface, cx, 132, 44)

        # Chispas decorativas
        comic.star_burst(surface, 150, 120, 22, 10, 5, comic.SUN1, comic.INK, ow=3)
        comic.star_burst(surface, WINDOW_WIDTH - 150, 96, 16, 7, 5, comic.PAPER, comic.INK, ow=2)
        comic.star_burst(surface, WINDOW_WIDTH - 96, 200, 12, 5, 4, comic.SUN1, comic.INK, ow=2)

        # Título tipo sticker
        comic.outlined_text(surface, "PokeFisi", 76, (cx, 250),
                            fill=comic.SUN1, outline=comic.INK, ow=5,
                            weight="bold", shadow=comic.RED, rotate=-3)

        # Subtítulo en banda
        comic.ribbon(surface, (cx, 320),
                     "Simulador de combates con I.A.", size=18,
                     fill=comic.BLUE, text_col=comic.PAPER)

        self.btn_battle.draw(surface)
        self.btn_tourney.draw(surface)
        self.btn_train.draw(surface)
        self.btn_delete.draw(surface)
        self.btn_exit.draw(surface)

        comic.outlined_text(
            surface,
            "Agentes: Aleatorio · Heurísticas · Minimax · Expectimax · Genético",
            13, (cx, WINDOW_HEIGHT - 26), fill=comic.PAPER, outline=comic.INK,
            ow=2, weight="semibold")

    def handle_event(self, event: pygame.event.Event):
        if self.btn_battle.handle_event(event):
            return "MODE_SELECT"
        if self.btn_tourney.handle_event(event):
            return "TOURNAMENT_SELECT"
        if self.btn_train.handle_event(event):
            return "TRAIN"
        if self.btn_delete.handle_event(event):
            return "DELETE"
        if self.btn_exit.handle_event(event):
            return "QUIT"
        return None
