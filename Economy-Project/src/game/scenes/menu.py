import math
from pygame import font, display, event, draw, time, QUIT, KEYDOWN, K_RETURN, K_ESCAPE, K_UP, K_DOWN, Surface, Rect, SRCALPHA
import pygame
import math
import sys
import os

# Ensure project src/game and src are on sys.path so `utils` and `entities` imports resolve
current_dir = os.path.dirname(os.path.abspath(__file__))
game_dir = os.path.dirname(current_dir)
src_dir = os.path.dirname(game_dir)
for p in (game_dir, src_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

from game.utils.renderer import Renderer

class Menu:
    """Menu scene adapted to the project's Game engine.

    Constructor now receives the `game` instance (the object created in
    `game/main.py`). The scene exposes `update()`, `draw(screen)` and
    `handle_event(event)` so `Game` can call them from its loop.
    """

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        # use centralized renderer for consistent visuals
        self.renderer = Renderer(self.screen)
        self.title_font = font.Font(None, 72)
        self.option_font = font.Font(None, 40)
        self.small_font = font.Font(None, 18)
        self.title = "💰 Economy Game"
        self.options = ["Iniciar Juego", "Tienda", "Inventario", "Misiones", "Ajustes", "Salir"]
        self.selected = 0
        self.clock = time.Clock()
        self.t = 0.0

    def _draw_options(self):
        start_y = self.height // 2 - (len(self.options) * 30)
        spacing = 72
        for i, opt in enumerate(self.options):
            is_selected = (i == self.selected)
            bg_color = (255, 200, 70, 220) if is_selected else (30, 25, 45, 160)
            pill_w, pill_h = self.width - 220, 56
            pill = Surface((pill_w, pill_h), SRCALPHA)
            draw.rect(pill, bg_color, pill.get_rect(), border_radius=28)
            px = (self.width - pill_w) // 2
            py = start_y + i * spacing
            self.screen.blit(pill, (px, py - 10))
            text_col = (30, 10, 0) if is_selected else (210, 210, 210)
            text_surf = self.option_font.render(opt, True, text_col)
            tr = text_surf.get_rect(center=(self.width // 2, py + 18))
            self.screen.blit(text_surf, tr)
            if is_selected:
                hint = self.small_font.render("ENTER para seleccionar • ↑/↓ para navegar • ESC salir", True, (200, 200, 200))
                hr = hint.get_rect(center=(self.width // 2, py + 56))
                self.screen.blit(hint, hr)

    def _option_rects(self):
        """Return a list of pygame.Rect covering each option's pill area.

        Rects are computed using the same layout values as `_draw_options()`
        so mouse hit-testing aligns with the visual elements.
        """
        rects = []
        start_y = self.height // 2 - (len(self.options) * 30)
        spacing = 72
        pill_w, pill_h = self.width - 220, 56
        px = (self.width - pill_w) // 2
        for i in range(len(self.options)):
            py = start_y + i * spacing
            rects.append(Rect(px, py - 10, pill_w, pill_h))
        return rects

    def _draw_background(self):
        self.t += 0.02
        r = int(18 + 28 * (1 + math.sin(self.t)) / 2)
        g = int(22 + 40 * (1 + math.sin(self.t + 1)) / 2)
        b = int(30 + 50 * (1 + math.sin(self.t + 2)) / 2)
        # smooth radial-ish gradient
        center = (self.width//2, self.height//3)
        base = Surface((self.width, self.height))
        for y in range(self.height):
            t = y / self.height
            rr = int(r + (30 * t))
            gg = int(g + (20 * t))
            bb = int(b + (10 * t))
            pygame.draw.line(base, (rr, gg, bb), (0, y), (self.width, y))
        self.screen.blit(base, (0,0))
        # soft vignette
        vignette = Surface((self.width, self.height), SRCALPHA)
        for i in range(0, 200, 4):
            alpha = int(200 * (i / 200) ** 2)
            draw.rect(vignette, (0, 0, 0, alpha), Rect(i, i, self.width - 2 * i, self.height - 2 * i), 1)
        self.screen.blit(vignette, (0, 0))

    def _draw_title(self):
        # use renderer text (with shadow)
        self.renderer.draw_text(self.title, (self.width//2, self.height//4), size=64, center=True)

    def _draw_options(self):
        start_y = self.height // 2 - (len(self.options) * 30)
        spacing = 72
        for i, opt in enumerate(self.options):
            is_selected = (i == self.selected)
            pill_w, pill_h = self.width - 260, 56
            px = (self.width - pill_w) // 2
            py = start_y + i * spacing
            # subtle scale/bright for selected
            if is_selected:
                self.renderer.draw_rounded_rect((px-6, py-14, pill_w+12, pill_h+8), (255, 220, 110), radius=32)
                self.renderer.draw_text(opt, (self.width//2, py+18), size=36, center=True)
            else:
                self.renderer.draw_rounded_rect((px, py-10, pill_w, pill_h), (40, 36, 52), radius=28)
                self.renderer.draw_text(opt, (self.width//2, py+18), size=30, center=True, color=(220,220,220))
            if is_selected:
                self.renderer.draw_text("ENTER para seleccionar • ↑/↓ navegar • ESC salir", (self.width//2, py+56), size=14, center=True, color=(200,200,200))

    def draw(self, screen=None):
        # allow Game loop to pass the screen or use stored one
        if screen is not None:
            self.screen = screen
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
            self.renderer.screen = self.screen

        self._draw_background()
        self._draw_title()
        self._draw_options()

    # Engine-compatible methods ------------------------------------------------
    def update(self):
        self.t += 0.0

    def handle_event(self, ev: pygame.event.Event):
        if ev.type == QUIT:
            self.game.quit()
            return
        if ev.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(ev.pos):
                    if rect.collidepoint(ev.pos):
                        self.selected = i
        if ev.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self._option_rects()):
                if rect.collidepoint(ev.pos):
                    self.selected = i
                    sel = self.options[self.selected]
                    if sel == "Iniciar Juego":
                        from scenes.gameplay import GameplayScene
                        self.game.change_scene(GameplayScene(self.game.screen))
                        return
                    if sel == "Tienda":
                        from scenes.shop import ShopScene
                        self.game.change_scene(ShopScene(self.game))
                        return
                    if sel == "Inventario":
                        self.game.change_scene(PlaceholderScene(self.game, "Inventario"))
                        return
                    if sel == "Misiones":
                        self.game.change_scene(PlaceholderScene(self.game, "Misiones"))
                        return
                    if sel == "Ajustes":
                        self.game.change_scene(PlaceholderScene(self.game, "Ajustes"))
                        return
                    if sel == "Salir":
                        self.game.quit()
                        return

        if ev.type == KEYDOWN:
            if ev.key == K_RETURN:
                sel = self.options[self.selected]
                if sel == "Iniciar Juego":
                    # instantiate GameplayScene from the game's scenes module
                    from scenes.gameplay import GameplayScene
                    self.game.change_scene(GameplayScene(self.game.screen))
                    return
                if sel == "Tienda":
                    from scenes.shop import ShopScene
                    self.game.change_scene(ShopScene(self.game))
                    return
                if sel == "Inventario":
                    self.game.change_scene(PlaceholderScene(self.game, "Inventario"))
                    return
                if sel == "Misiones":
                    self.game.change_scene(PlaceholderScene(self.game, "Misiones"))
                    return
                if sel == "Ajustes":
                    self.game.change_scene(PlaceholderScene(self.game, "Ajustes"))
                    return
                if sel == "Salir":
                    self.game.quit()
                    return
            if ev.key == K_ESCAPE:
                self.game.quit()
                return
            if ev.key == K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                return
            if ev.key == K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                return
    # end engine-compatible methods --------------------------------------------

# Backwards-compatible aliases
class MenuScene(Menu):
    pass

class menuscene(MenuScene):
    pass


class PlaceholderScene:
    """Simple scene used for unimplemented menu entries (shop, inventory...).

    Shows a title and instructions to return to the menu.
    """
    def __init__(self, game, title: str):
        self.game = game
        self.screen = game.screen
        self.title = title
        self.renderer = Renderer(self.screen)
        self.clock = time.Clock()

    def update(self):
        pass

    def draw(self, screen=None):
        if screen is not None:
            self.screen = screen
            self.renderer.screen = screen
        self.renderer.clear((12, 14, 20))
        self.renderer.draw_text(self.title, (self.screen.get_width()//2, 120), size=48, center=True)
        self.renderer.draw_text("(Presiona ESC para volver al menú)", (self.screen.get_width()//2, 200), size=20, center=True)
        self.renderer.update()

    def handle_event(self, ev: pygame.event.Event):
        if ev.type == KEYDOWN and ev.key == K_ESCAPE:
            # go back to menu
            self.game.change_scene(Menu(self.game))
        if ev.type == QUIT:
            self.game.quit()