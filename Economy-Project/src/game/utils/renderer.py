import pygame
import os
import math
import pygame
from pygame import Surface

class Renderer:
    """Utility renderer with higher-quality helpers.

    - Safe font loading with fallbacks
    - Text with optional shadow and centering
    - Rounded rects, sprites, health bars
    - Basic image cache
    """

    def __init__(self, screen: Surface):
        self.screen = screen
        self._fonts = {}
        self._images = {}
        # default base font
        try:
            self._fonts['base'] = pygame.font.Font(None, 28)
        except Exception:
            self._fonts['base'] = pygame.font.SysFont('arial', 28)

    def load_font(self, size: int, name: str = None):
        key = f"{name or 'default'}-{size}"
        if key in self._fonts:
            return self._fonts[key]
        try:
            f = pygame.font.Font(name, size) if name else pygame.font.Font(None, size)
        except Exception:
            f = pygame.font.SysFont('arial', size)
        self._fonts[key] = f
        return f

    def clear(self, color=(18, 18, 24)):
        self.screen.fill(color)

    def draw_text(self, text, pos, color=(255,255,255), size=28, center=False, shadow=True):
        font = self.load_font(size)
        surf = font.render(text, True, color)
        if shadow:
            sh = font.render(text, True, (0,0,0))
            if center:
                r = sh.get_rect(center=pos)
                self.screen.blit(sh, (r.x+2, r.y+2))
            else:
                self.screen.blit(sh, (pos[0]+2, pos[1]+2))

        if center:
            r = surf.get_rect(center=pos)
            self.screen.blit(surf, r)
        else:
            self.screen.blit(surf, pos)

    def draw_rect(self, rect, color):
        pygame.draw.rect(self.screen, color, rect)

    def draw_rounded_rect(self, rect, color, radius=12):
        try:
            pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        except Exception:
            # fallback
            pygame.draw.rect(self.screen, color, rect)

    def load_image(self, path, colorkey=None, scale=None):
        if not path:
            return None
        key = f"{path}-{scale}"
        if key in self._images:
            return self._images[key]
        if not os.path.isabs(path):
            # try relative to project root
            base = os.path.dirname(__file__)
            path = os.path.join(base, '..', '..', path)
            path = os.path.normpath(path)
        try:
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.smoothscale(img, scale)
            if colorkey is not None:
                img.set_colorkey(colorkey)
        except Exception:
            img = None
        self._images[key] = img
        return img

    def draw_sprite(self, image, pos):
        if image is None:
            return
        rect = image.get_rect(center=pos)
        self.screen.blit(image, rect)

    def draw_health_bar(self, x, y, w, h, pct, bg=(80,80,80), fg=(200,50,50)):
        pct = max(0.0, min(1.0, pct))
        self.draw_rounded_rect((x, y, w, h), bg, radius=h//2)
        inner_w = int((w-4) * pct)
        if inner_w > 0:
            self.draw_rounded_rect((x+2, y+2, inner_w, h-4), fg, radius=(h-4)//2)

    def update(self):
        pygame.display.flip()