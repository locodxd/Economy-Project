"""
✨ PARTICLE SYSTEM - Sistema de partículas y efectos visuales
"""

import pygame
import random
import math
from typing import List, Tuple


class Particle:
    """Partícula individual"""
    
    def __init__(self, x, y, vx, vy, color, size, lifetime, gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.alpha = 255
    
    def update(self, dt=1):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        # Fade out
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
    
    def is_alive(self) -> bool:
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.is_alive():
            color = (*self.color[:3], self.alpha)
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(self.size), int(self.size)), int(self.size))
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class ParticleEmitter:
    """Emisor de partículas"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles: List[Particle] = []
    
    def emit(self, count, color_range, speed_range, size_range, lifetime_range, angle_range=(0, 360), gravity=0):
        """Emite partículas"""
        for _ in range(count):
            angle = random.uniform(*angle_range) * (math.pi / 180)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = tuple(random.randint(c1, c2) for c1, c2 in zip(color_range[0], color_range[1]))
            size = random.uniform(*size_range)
            lifetime = random.uniform(*lifetime_range)
            
            particle = Particle(self.x, self.y, vx, vy, color, size, lifetime, gravity)
            self.particles.append(particle)
    
    def update(self):
        """Actualiza partículas"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
    
    def draw(self, screen):
        """Dibuja partículas"""
        for particle in self.particles:
            particle.draw(screen)
    
    def set_position(self, x, y):
        """Actualiza posición del emisor"""
        self.x = x
        self.y = y


class ParticleEffects:
    """Efectos predefinidos de partículas"""
    
    @staticmethod
    def coin_collect(emitter: ParticleEmitter):
        """Efecto de recolectar moneda"""
        emitter.emit(
            count=15,
            color_range=[(255, 215, 0), (255, 255, 100)],
            speed_range=(2, 6),
            size_range=(3, 7),
            lifetime_range=(15, 30),
            angle_range=(0, 360),
            gravity=0.2
        )
    
    @staticmethod
    def level_up(emitter: ParticleEmitter):
        """Efecto de subir de nivel"""
        emitter.emit(
            count=40,
            color_range=[(100, 200, 255), (200, 100, 255)],
            speed_range=(3, 8),
            size_range=(4, 10),
            lifetime_range=(30, 60),
            angle_range=(0, 360),
            gravity=-0.1
        )
    
    @staticmethod
    def damage(emitter: ParticleEmitter):
        """Efecto de daño"""
        emitter.emit(
            count=20,
            color_range=[(255, 50, 50), (255, 100, 100)],
            speed_range=(2, 5),
            size_range=(3, 6),
            lifetime_range=(10, 20),
            angle_range=(0, 360),
            gravity=0.3
        )
    
    @staticmethod
    def heal(emitter: ParticleEmitter):
        """Efecto de curación"""
        emitter.emit(
            count=25,
            color_range=[(50, 255, 50), (100, 255, 150)],
            speed_range=(1, 4),
            size_range=(4, 8),
            lifetime_range=(20, 40),
            angle_range=(0, 360),
            gravity=-0.2
        )
    
    @staticmethod
    def sparkle(emitter: ParticleEmitter):
        """Efecto de brillo"""
        emitter.emit(
            count=10,
            color_range=[(255, 255, 200), (255, 255, 255)],
            speed_range=(1, 3),
            size_range=(2, 5),
            lifetime_range=(15, 25),
            angle_range=(0, 360),
            gravity=0
        )
    
    @staticmethod
    def explosion(emitter: ParticleEmitter):
        """Efecto de explosión"""
        emitter.emit(
            count=50,
            color_range=[(255, 100, 0), (255, 200, 50)],
            speed_range=(5, 12),
            size_range=(5, 12),
            lifetime_range=(20, 40),
            angle_range=(0, 360),
            gravity=0.3
        )
    
    @staticmethod
    def trail(emitter: ParticleEmitter, color=(200, 200, 255)):
        """Efecto de estela de movimiento"""
        emitter.emit(
            count=3,
            color_range=[color, tuple(min(c + 30, 255) for c in color)],
            speed_range=(0, 1),
            size_range=(4, 7),
            lifetime_range=(10, 20),
            angle_range=(0, 360),
            gravity=0
        )


class ParticleManager:
    """Gestor global de partículas"""
    
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
    
    def create_emitter(self, x, y) -> ParticleEmitter:
        """Crea un nuevo emisor"""
        emitter = ParticleEmitter(x, y)
        self.emitters.append(emitter)
        return emitter
    
    def create_effect(self, x, y, effect_type: str):
        """Crea un efecto predefinido"""
        emitter = self.create_emitter(x, y)
        effect_func = getattr(ParticleEffects, effect_type, None)
        if effect_func:
            effect_func(emitter)
    
    def update(self):
        """Actualiza todos los emisores"""
        for emitter in self.emitters:
            emitter.update()
        # Eliminar emisores sin partículas
        self.emitters = [e for e in self.emitters if len(e.particles) > 0]
    
    def draw(self, screen):
        """Dibuja todas las partículas"""
        for emitter in self.emitters:
            emitter.draw(screen)
    
    def clear(self):
        """Limpia todos los emisores"""
        self.emitters.clear()


class SpriteAnimator:
    """Animador de sprites"""
    
    def __init__(self, frames: List[pygame.Surface], fps: int = 10):
        self.frames = frames
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.current_frame = 0
        self.time_accumulator = 0
        self.loop = True
        self.playing = True
    
    def update(self, dt: float):
        """Actualiza animación"""
        if not self.playing:
            return
        
        self.time_accumulator += dt
        if self.time_accumulator >= self.frame_duration:
            self.time_accumulator = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.playing = False
    
    def get_current_frame(self) -> pygame.Surface:
        """Retorna frame actual"""
        return self.frames[self.current_frame]
    
    def reset(self):
        """Reinicia animación"""
        self.current_frame = 0
        self.time_accumulator = 0
        self.playing = True
    
    def pause(self):
        self.playing = False
    
    def play(self):
        self.playing = True


def create_simple_sprite(width: int, height: int, color: Tuple[int, int, int], shape="rect") -> pygame.Surface:
    """Crea un sprite simple"""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    if shape == "rect":
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=4)
    elif shape == "circle":
        pygame.draw.circle(surf, color, (width//2, height//2), min(width, height)//2)
    elif shape == "triangle":
        points = [(width//2, 0), (0, height), (width, height)]
        pygame.draw.polygon(surf, color, points)
    
    return surf


def create_gradient_sprite(width: int, height: int, color1: Tuple, color2: Tuple) -> pygame.Surface:
    """Crea sprite con gradiente"""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y in range(height):
        t = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    
    return surf
