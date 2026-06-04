import sys
import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, BG_COLOR
from engine.loader import load_moves, build_team
from engine.state import BattleState
from ai import registry


class GameManager:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("PokeFisi")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.all_moves = load_moves()

        self._state_name = "MENU"
        self._screen = None
        self._mode_config = None   # datos de configuración entre pantallas
        self._load_screen("MENU")

    def _load_screen(self, state_name: str, *args):
        self._state_name = state_name
        if state_name == "MENU":
            from gui.screens.main_menu import MainMenu
            self._screen = MainMenu()

        elif state_name == "MODE_SELECT":
            from gui.screens.mode_select import ModeSelect
            self._screen = ModeSelect()

        elif state_name == "TRAIN":
            from gui.screens.train_screen import TrainScreen
            self._screen = TrainScreen()

        elif state_name == "POKEMON_SELECT":
            mode, team_size, ai1_idx, ai2_idx = args
            self._mode_config = (mode, team_size, ai1_idx, ai2_idx)
            from gui.screens.pokemon_select import PokemonSelect
            self._screen = PokemonSelect(mode, team_size)

        elif state_name == "BATTLE":
            team1_ids, team2_ids = args
            mode, team_size, ai1_idx, ai2_idx = self._mode_config

            team1 = build_team(team1_ids, self.all_moves)

            # Derivar las factories del snapshot actual del registro (puede haberse
            # refrescado tras entrenar en la GUI). El mismo orden que vio ModeSelect.
            factories = [factory for _, factory in registry.AI_REGISTRY]

            if mode == "human_vs_ai":
                team2  = build_team(team2_ids, self.all_moves)
                agent1 = None
                agent2 = factories[ai2_idx]()
                label1 = "Jugador"
                label2 = agent2.name
            else:
                team2  = build_team(team2_ids, self.all_moves)
                agent1 = factories[ai1_idx]()
                agent2 = factories[ai2_idx]()
                label1 = agent1.name
                label2 = agent2.name

            state = BattleState(team1, team2)
            from gui.screens.battle_screen import BattleScreen
            self._screen = BattleScreen(state, agent1, agent2, mode, label1, label2)

        elif state_name == "RESULTS":
            battle_screen = self._screen
            from gui.screens.results_screen import ResultsScreen
            self._screen = ResultsScreen(battle_screen.winner, battle_screen.state,
                                         battle_screen.label1, battle_screen.label2)

    def _random_ids(self, size: int) -> list[int]:
        import random
        return random.sample(range(1, 31), size)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break

                result = self._screen.handle_event(event)
                if result:
                    running = self._process_result(result)
                    if not running:
                        break

            if hasattr(self._screen, "update"):
                self._screen.update(dt)

            self._screen.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _process_result(self, result) -> bool:
        if result == "QUIT":
            return False

        if isinstance(result, tuple):
            name = result[0]
            if name == "POKEMON_SELECT":
                _, mode, team_size, ai1_idx, ai2_idx = result
                self._load_screen("POKEMON_SELECT", mode, team_size, ai1_idx, ai2_idx)
            elif name == "BATTLE":
                _, team1_ids, team2_ids = result
                self._load_screen("BATTLE", team1_ids, team2_ids)
            else:
                self._load_screen(name, *result[1:])
        else:
            if result == "RESULTS":
                self._load_screen("RESULTS")
            else:
                self._load_screen(result)

        return True
