"""
🛒 SHOP SCENE - Escena de tienda mejorada con sistema de economía
"""

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

from utils.renderer import Renderer
from utils.particles import ParticleManager, ParticleEffects


class ShopScene:
    """Escena de tienda interactiva"""
    
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.width, self.height = self.screen.get_size()
        self.renderer = Renderer(self.screen)
        self.particles = ParticleManager()
        
        # Referencias a sistemas del juego
        self.economy = game.economy
        self.player = game.economy.player
        
        # UI State
        self.selected_category = "all"
        self.selected_item = None
        self.scroll_offset = 0
        self.categories = ["all", "weapon", "armor", "consumable", "material"]
        self.category_names = {
            "all": "Todo",
            "weapon": "Armas",
            "armor": "Armaduras",
            "consumable": "Consumibles",
            "material": "Materiales"
        }
        
    def get_items_by_category(self):
        """Filtra items por categoría"""
        items = []
        for item_id, item_data in self.economy.items_catalog.items():
            if self.selected_category == "all" or item_data.get("type") == self.selected_category:
                items.append((item_id, item_data))
        return items
    
    def draw(self, screen=None):
        if screen:
            self.screen = screen
            self.renderer.screen = screen
        
        # Fondo
        self.renderer.clear((12, 14, 20))
        
        # Título
        self.renderer.draw_text(
            "🛒 TIENDA",
            (self.width//2, 40),
            size=48,
            center=True,
            color=(255, 220, 100)
        )
        
        # Balance del jugador
        balance_text = f"💰 ${self.player.coins}  💎 {self.player.gems} gemas"
        self.renderer.draw_text(
            balance_text,
            (self.width//2, 90),
            size=24,
            center=True,
            color=(200, 200, 200)
        )
        
        # Categorías
        cat_y = 140
        cat_x_start = 100
        cat_spacing = 150
        for i, cat in enumerate(self.categories):
            x = cat_x_start + i * cat_spacing
            is_selected = cat == self.selected_category
            
            color = (255, 200, 70) if is_selected else (100, 100, 120)
            self.renderer.draw_rounded_rect(
                (x, cat_y, 130, 35),
                color if is_selected else (40, 40, 50),
                radius=8
            )
            
            text_color = (20, 20, 20) if is_selected else (180, 180, 180)
            self.renderer.draw_text(
                self.category_names[cat],
                (x + 65, cat_y + 18),
                size=18,
                center=True,
                color=text_color,
                shadow=False
            )
        
        # Lista de items
        items = self.get_items_by_category()
        item_y = 200
        item_height = 80
        visible_items = 6
        
        for i, (item_id, item_data) in enumerate(items[self.scroll_offset:self.scroll_offset + visible_items]):
            y = item_y + i * item_height
            is_selected = item_id == self.selected_item
            
            # Fondo del item
            bg_color = (60, 65, 75) if is_selected else (35, 38, 45)
            self.renderer.draw_rounded_rect(
                (50, y, self.width - 100, item_height - 10),
                bg_color,
                radius=12
            )
            
            # Nombre y precio
            name = item_data.get("name", item_id)
            price = item_data.get("price", 0)
            
            self.renderer.draw_text(
                name,
                (70, y + 15),
                size=22,
                color=(255, 255, 200) if is_selected else (220, 220, 220)
            )
            
            # Descripción
            desc = item_data.get("description", "")
            self.renderer.draw_text(
                desc,
                (70, y + 40),
                size=16,
                color=(150, 150, 150),
                shadow=False
            )
            
            # Precio
            price_text = f"${price}"
            self.renderer.draw_text(
                price_text,
                (self.width - 150, y + 25),
                size=24,
                color=(100, 255, 100) if self.player.can_afford(price) else (255, 100, 100)
            )
            
            # Botón comprar si está seleccionado
            if is_selected:
                btn_x = self.width - 250
                btn_y = y + 15
                can_buy = self.player.can_afford(price)
                btn_color = (80, 200, 80) if can_buy else (120, 60, 60)
                
                self.renderer.draw_rounded_rect(
                    (btn_x, btn_y, 80, 35),
                    btn_color,
                    radius=8
                )
                
                self.renderer.draw_text(
                    "COMPRAR" if can_buy else "SIN $",
                    (btn_x + 40, btn_y + 18),
                    size=16,
                    center=True,
                    color=(255, 255, 255),
                    shadow=False
                )
        
        # Instrucciones
        instructions = "↑↓ Navegar  •  ← → Categoría  •  ENTER Comprar  •  ESC Volver"
        self.renderer.draw_text(
            instructions,
            (self.width//2, self.height - 30),
            size=16,
            center=True,
            color=(150, 150, 150),
            shadow=False
        )
        
        # Partículas
        self.particles.draw(self.screen)
        self.renderer.update()
    
    def update(self):
        self.particles.update()
    
    def handle_event(self, ev: pygame.event.Event):
        items = self.get_items_by_category()
        
        if ev.type == pygame.QUIT:
            self.game.quit()
            return
        
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                # Volver al menú
                from scenes.menu import Menu
                self.game.change_scene(Menu(self.game))
                return
            
            # Navegar categorías
            if ev.key == pygame.K_LEFT:
                idx = self.categories.index(self.selected_category)
                self.selected_category = self.categories[(idx - 1) % len(self.categories)]
                self.selected_item = None
                self.scroll_offset = 0
            
            elif ev.key == pygame.K_RIGHT:
                idx = self.categories.index(self.selected_category)
                self.selected_category = self.categories[(idx + 1) % len(self.categories)]
                self.selected_item = None
                self.scroll_offset = 0
            
            # Navegar items
            elif ev.key == pygame.K_UP:
                if not self.selected_item and items:
                    self.selected_item = items[0][0]
                elif items:
                    current_idx = next((i for i, (iid, _) in enumerate(items) if iid == self.selected_item), 0)
                    new_idx = (current_idx - 1) % len(items)
                    self.selected_item = items[new_idx][0]
            
            elif ev.key == pygame.K_DOWN:
                if not self.selected_item and items:
                    self.selected_item = items[0][0]
                elif items:
                    current_idx = next((i for i, (iid, _) in enumerate(items) if iid == self.selected_item), 0)
                    new_idx = (current_idx + 1) % len(items)
                    self.selected_item = items[new_idx][0]
            
            # Comprar
            elif ev.key == pygame.K_RETURN and self.selected_item:
                success, msg = self.economy.buy_item(self.selected_item, 1)
                if success:
                    # Efecto de compra exitosa
                    self.particles.create_effect(self.width//2, self.height//2, "coin_collect")
                    self.selected_item = None  # Reset selection after purchase
                print(msg)  # En producción usar un sistema de notificaciones

# Alias backward compatibility
Shop = ShopScene

    def run(self, screen: Surface):
        running = True
        while running:
            running = self.handle_input()
            self.display(screen)
            self.renderer.update(screen)

def main():
    player = Player()
    shop = Shop(player)
    screen = Surface((800, 600))
    shop.run(screen)

if __name__ == "__main__":
    main()