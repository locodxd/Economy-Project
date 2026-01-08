"""
🎮 GAME ECONOMY MANAGER - Sistema de economía adaptado para pygame
Adaptación del sistema de economía avanzado del bot de Discord
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class PlayerEconomy:
    """Datos económicos del jugador"""
    player_name: str
    coins: int = 1000
    bank: int = 0
    gems: int = 0
    level: int = 1
    xp: int = 0
    total_earned: int = 0
    total_spent: int = 0
    
    # Inventario
    inventory: Dict[str, int] = None
    equipment: Dict[str, str] = None
    
    # Cooldowns
    last_daily: Optional[float] = None
    last_work: Optional[float] = None
    last_mission: Optional[float] = None
    
    # Stats
    daily_streak: int = 0
    missions_completed: int = 0
    items_crafted: int = 0
    enemies_defeated: int = 0
    
    # Progression
    skill_points: int = 0
    skills: Dict[str, int] = None  # combat:5, mining:3, etc.
    achievements: List[str] = None
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = {}
        if self.equipment is None:
            self.equipment = {"weapon": None, "armor": None, "accessory": None}
        if self.skills is None:
            self.skills = {"combat": 1, "mining": 1, "fishing": 1, "crafting": 1}
        if self.achievements is None:
            self.achievements = []
    
    @property
    def xp_to_next_level(self) -> int:
        return self.level * 100
    
    def add_xp(self, amount: int) -> List[str]:
        """Añade XP y retorna lista de level ups"""
        self.xp += amount
        levels = []
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.skill_points += 3
            levels.append(f"¡LEVEL UP! Ahora eres nivel {self.level}")
        return levels
    
    def can_afford(self, amount: int) -> bool:
        return self.coins >= amount
    
    def spend(self, amount: int) -> bool:
        if self.can_afford(amount):
            self.coins -= amount
            self.total_spent += amount
            return True
        return False
    
    def earn(self, amount: int):
        self.coins += amount
        self.total_earned += amount
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        return self.inventory.get(item_id, 0) >= quantity
    
    def add_item(self, item_id: str, quantity: int = 1):
        self.inventory[item_id] = self.inventory.get(item_id, 0) + quantity
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        if self.has_item(item_id, quantity):
            self.inventory[item_id] -= quantity
            if self.inventory[item_id] <= 0:
                del self.inventory[item_id]
            return True
        return False


class GameEconomyManager:
    """Gestor de economía del juego"""
    
    def __init__(self, save_file: str = "game_save.json"):
        self.save_path = Path("Economy-Project/Economy-Project/database") / save_file
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        self.player: Optional[PlayerEconomy] = None
        self.items_catalog = self._load_items_catalog()
    
    def _load_items_catalog(self) -> Dict:
        """Carga el catálogo de items"""
        return {
            # Consumibles
            "health_potion": {
                "name": "Poción de Vida",
                "description": "Restaura 50 HP",
                "price": 50,
                "type": "consumable",
                "effect": "heal_50"
            },
            "mana_potion": {
                "name": "Poción de Maná",
                "description": "Restaura 30 MP",
                "price": 40,
                "type": "consumable",
                "effect": "mana_30"
            },
            
            # Armas
            "wooden_sword": {
                "name": "Espada de Madera",
                "description": "Arma básica. ATK +5",
                "price": 100,
                "type": "weapon",
                "stats": {"attack": 5}
            },
            "iron_sword": {
                "name": "Espada de Hierro",
                "description": "Arma común. ATK +12",
                "price": 500,
                "type": "weapon",
                "stats": {"attack": 12}
            },
            "steel_sword": {
                "name": "Espada de Acero",
                "description": "Arma rara. ATK +25",
                "price": 2000,
                "type": "weapon",
                "stats": {"attack": 25}
            },
            
            # Armaduras
            "leather_armor": {
                "name": "Armadura de Cuero",
                "description": "Protección básica. DEF +8",
                "price": 150,
                "type": "armor",
                "stats": {"defense": 8}
            },
            "iron_armor": {
                "name": "Armadura de Hierro",
                "description": "Protección sólida. DEF +20",
                "price": 800,
                "type": "armor",
                "stats": {"defense": 20}
            },
            
            # Materiales
            "wood": {"name": "Madera", "price": 5, "type": "material"},
            "stone": {"name": "Piedra", "price": 3, "type": "material"},
            "iron_ore": {"name": "Mineral de Hierro", "price": 15, "type": "material"},
            "gold_ore": {"name": "Mineral de Oro", "price": 50, "type": "material"},
            
            # Especiales
            "xp_boost": {
                "name": "Boost de XP",
                "description": "2x XP por 10 minutos",
                "price": 500,
                "type": "boost",
                "duration": 600
            }
        }
    
    def load_player(self, player_name: str = "Player") -> PlayerEconomy:
        """Carga o crea datos del jugador"""
        if self.save_path.exists():
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.player = PlayerEconomy(**data)
        else:
            self.player = PlayerEconomy(player_name=player_name)
            self.save_player()
        return self.player
    
    def save_player(self):
        """Guarda datos del jugador"""
        if self.player:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.player), f, indent=2)
    
    def get_item_info(self, item_id: str) -> Optional[Dict]:
        return self.items_catalog.get(item_id)
    
    def can_collect_daily(self) -> bool:
        """Verifica si puede cobrar daily"""
        if not self.player.last_daily:
            return True
        elapsed = time.time() - self.player.last_daily
        return elapsed >= 86400  # 24 horas
    
    def collect_daily(self) -> tuple[int, int]:
        """Cobra daily y retorna (coins, streak)"""
        base_reward = 500
        streak_bonus = min(self.player.daily_streak * 50, 1000)
        total = base_reward + streak_bonus
        
        self.player.earn(total)
        self.player.daily_streak += 1
        self.player.last_daily = time.time()
        self.save_player()
        
        return total, self.player.daily_streak
    
    def can_work(self) -> bool:
        """Verifica si puede trabajar"""
        if not self.player.last_work:
            return True
        elapsed = time.time() - self.player.last_work
        return elapsed >= 3600  # 1 hora
    
    def work(self) -> Dict:
        """Trabaja y retorna recompensa"""
        import random
        jobs = [
            {"name": "Minero", "min": 100, "max": 300, "xp": 10},
            {"name": "Pescador", "min": 80, "max": 250, "xp": 8},
            {"name": "Herrero", "min": 150, "max": 400, "xp": 15},
            {"name": "Comerciante", "min": 200, "max": 500, "xp": 20},
            {"name": "Aventurero", "min": 300, "max": 800, "xp": 30}
        ]
        
        job = random.choice(jobs)
        coins = random.randint(job["min"], job["max"])
        xp = job["xp"]
        
        self.player.earn(coins)
        levels = self.player.add_xp(xp)
        self.player.last_work = time.time()
        self.save_player()
        
        return {
            "job": job["name"],
            "coins": coins,
            "xp": xp,
            "levels": levels
        }
    
    def buy_item(self, item_id: str, quantity: int = 1) -> tuple[bool, str]:
        """Compra item y retorna (éxito, mensaje)"""
        item_info = self.get_item_info(item_id)
        if not item_info:
            return False, "Item no existe"
        
        total_cost = item_info["price"] * quantity
        if not self.player.can_afford(total_cost):
            return False, f"Necesitas ${total_cost} (tienes ${self.player.coins})"
        
        self.player.spend(total_cost)
        self.player.add_item(item_id, quantity)
        self.save_player()
        
        return True, f"Compraste {quantity}x {item_info['name']}"
    
    def sell_item(self, item_id: str, quantity: int = 1) -> tuple[bool, str]:
        """Vende item y retorna (éxito, mensaje)"""
        item_info = self.get_item_info(item_id)
        if not item_info:
            return False, "Item no existe"
        
        if not self.player.has_item(item_id, quantity):
            return False, "No tienes suficientes items"
        
        sell_price = int(item_info["price"] * 0.6 * quantity)  # 60% del precio
        self.player.remove_item(item_id, quantity)
        self.player.earn(sell_price)
        self.save_player()
        
        return True, f"Vendiste {quantity}x {item_info['name']} por ${sell_price}"
