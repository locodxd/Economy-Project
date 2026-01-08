from random import randint, uniform
import math
import pygame
import sys
import os

# Ensure project src/game and src are on sys.path so `utils` and `entities` imports resolve
current_dir = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.dirname(current_dir)
src_dir = os.path.dirname(game_dir)
for p in (game_dir, src_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from game.entities.player import Player
from game.entities.npc import NPC
from game.utils.renderer import Renderer


class GameplayScene:
    """Simple gameplay scene compatible with the project's entities.

    This scene uses relative imports and a minimal loop so it can be
    instantiated by other parts of the project without causing import
    errors.
    """

    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        # Use Player from entities; supply a name required by the class
        self.player = Player("Heroe")
        # track a simple position for rendering/movement
        self.player_pos = [self.width // 2, self.height // 2]
        # movement flags so keydown/keyup works reliably
        self.move_flags = {"left": False, "right": False, "up": False, "down": False}

        # Create a few NPCs with simple dialogues and random positions
        sample_dialogue = ["Hola!", "Buenas.", "¿Quieres comerciar?", "Suerte!"]
        self.npcs = [NPC(f"NPC{i}", sample_dialogue, randint(50, self.width - 50), randint(50, self.height - 50)) for i in range(6)]
        # per-npc state for wander behavior
        self.npc_state = {}
        for npc in self.npcs:
            self.npc_state[npc] = {
                "speed": uniform(0.3, 1.2),
                "target": (randint(40, self.width-40), randint(40, self.height-40)),
                "timer": randint(60, 240)
            }

        # Renderer expects the screen in its constructor
        self.renderer = Renderer(self.screen)

        self.clock = pygame.time.Clock()
        self.running = True

    def handle_input(self):
        # Movement based on flags set in handle_event for reliable control
        speed = 4
        if self.move_flags["left"]:
            self.player_pos[0] -= speed
        if self.move_flags["right"]:
            self.player_pos[0] += speed
        if self.move_flags["up"]:
            self.player_pos[1] -= speed
        if self.move_flags["down"]:
            self.player_pos[1] += speed

        # clamp to screen
        self.player_pos[0] = max(8, min(self.width-8, self.player_pos[0]))
        self.player_pos[1] = max(8, min(self.height-8, self.player_pos[1]))

    def update(self):
        # NPC behaviour: wander towards a target, avoid clustering, sometimes approach player
        for npc in self.npcs:
            st = self.npc_state[npc]
            tx, ty = st["target"]
            # small chance to retarget or when close
            dist = math.hypot(tx - npc.x, ty - npc.y)
            if dist < 12 or st["timer"] <= 0:
                st["target"] = (randint(40, self.width-40), randint(40, self.height-40))
                st["timer"] = randint(60, 240)

            # vector toward target
            dx = st["target"][0] - npc.x
            dy = st["target"][1] - npc.y
            mag = math.hypot(dx, dy) or 1.0
            vx = (dx / mag) * st["speed"]
            vy = (dy / mag) * st["speed"]

            # avoidance: steer away slightly from nearby npcs
            for other in self.npcs:
                if other is npc:
                    continue
                odx = npc.x - other.x
                ody = npc.y - other.y
                od = math.hypot(odx, ody)
                if od < 28 and od > 0:
                    vx += (odx / od) * 0.8
                    vy += (ody / od) * 0.8

            # occasional curious behavior: approach player if close
            pdx = self.player_pos[0] - npc.x
            pdy = self.player_pos[1] - npc.y
            pd = math.hypot(pdx, pdy)
            if pd < 160 and randint(0, 100) < 12:
                vx += (pdx / (pd or 1)) * 0.6
                vy += (pdy / (pd or 1)) * 0.6

            # apply movement
            nx = npc.x + vx
            ny = npc.y + vy
            # clamp
            nx = max(8, min(self.width-8, nx))
            ny = max(8, min(self.height-8, ny))
            npc.move(nx, ny)
            st["timer"] -= 1

    def draw(self, screen=None):
        # allow Game loop to pass the screen
        if screen is not None:
            self.screen = screen
            self.width, self.height = screen.get_size()
            # update renderer to use the new screen reference
            self.renderer.screen = self.screen

        # clear screen
        self.renderer.clear((18, 18, 24))

        # draw player as a rect and name/coins
        p_rect = (self.player_pos[0] - 12, self.player_pos[1] - 12, 24, 24)
        self.renderer.draw_rect(p_rect, (60, 180, 80))
        self.renderer.draw_text(f"{self.player.name} Lv{self.player.level} ❤️{self.player.health}", (10, 10), (220, 220, 220))

        # draw NPCs
        for npc in self.npcs:
            nrect = (npc.x - 10, npc.y - 10, 20, 20)
            self.renderer.draw_rect(nrect, (180, 120, 60))
            self.renderer.draw_text(npc.name, (npc.x + 12, npc.y - 8), (200, 200, 200))

        # update renderer (flips display)
        self.renderer.update()

    def handle_event(self, ev: pygame.event.Event):
        # minimal handler so Game.handle_events can forward events
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            # if the scene is running a self-contained loop, stop it
            self.running = False
        # otherwise ignore events (Game manages quit)

    def run(self):
        # A simple loop; callers can instead call update/draw themselves
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    self.running = False

            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()