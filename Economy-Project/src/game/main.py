import pygame
import sys
from pathlib import Path

# Añadir core al path para importar economy y missions
sys.path.insert(0, str(Path(__file__).parent.parent))

from game_config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from scenes.menu import MenuScene
from scenes.gameplay import GameplayScene
from core.game_economy import GameEconomyManager
from core.mission_system import MissionManager
from game.utils.renderer import Renderer

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Economy Game - RPG Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inicializar sistemas
        self.economy = GameEconomyManager()
        self.economy.load_player("Hero")
        self.mission_manager = MissionManager()
        
        self.current_scene = MenuScene(self)

    def run(self):
        while self.running:
            self.handle_events()
            self.current_scene.update()
            self.current_scene.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.economy.save_player()  # Guardar antes de salir
            self.current_scene.handle_event(event)

    def change_scene(self, new_scene):
        self.current_scene = new_scene

    def quit(self):
        self.economy.save_player()  # Guardar progreso
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()