"""
sistema de gifs con tenor pero sin tanto rollo
basicamente cachea los gifs para no estar spameando el api
"""

import aiohttp
import asyncio
import random
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TenorCore:
    """maneja los gifs de tenor con cache y esas cosas"""
    
    def __init__(self, api_key: str = None):
        # si no se pasa api_key, intenta obtenerla del .env
        self.api_key = api_key or os.getenv('TENOR_API_KEY')
        
        if not self.api_key:
            logger.warning("no hay TENOR_API_KEY configurada, los gifs no van a funcionar")
            logger.warning("ejecuta configurator.py para configurar la api key de tenor")
        
        self.api_url = "https://tenor.googleapis.com/v2/search"
        self.cache: Dict[str, List[str]] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        # cada categoria tiene varios terminos para buscar random
        self.categories = {
            "money": ["money rain", "cash money", "rich money"],
            "work": ["working hard", "office work", "busy working"],
            "win": ["celebration", "victory", "success"],
            "lose": ["crying", "sad broke", "失敗"],
            "slots": ["slot machine", "casino slots", "jackpot"],
            "dice": ["rolling dice", "dice roll", "lucky dice"],
            "cards": ["poker cards", "blackjack", "shuffling cards"],
            "roulette": ["roulette", "casino roulette", "roulette wheel"],
            "jackpot": ["jackpot win", "big win", "winner"],
            "broke": ["broke", "no money", "empty wallet"],
            "robbery": ["robbery", "heist", "stealing"],
            "police": ["police chase", "cops", "arrested"],
            "escape": ["running away", "escape", "getaway"],
            "fight": ["fighting", "punch", "combat"],
            "explosion": ["explosion", "boom", "kaboom"],
            "victory": ["epic victory", "winner", "champion"],
            "dragon": ["dragon", "dragon fire", "wyrm"],
            "dungeon": ["dungeon", "dark cave", "exploration"],
            "treasure": ["treasure chest", "gold", "loot"],
            "monster": ["monster", "creature", "beast"],
            "magic": ["magic spell", "wizard", "sorcery"],
            "boss": ["boss fight", "epic boss", "final boss"],
            "death": ["death", "game over", "defeated"],
            "levelup": ["level up", "power up", "upgrade"],
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """crea session si no existe"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """cierra la session cuando ya no se usa"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_gif(self, category: str) -> Optional[str]:
        """
        busca un gif de la categoria
        si no esta en cache, lo busca en tenor
        """
        if category not in self.categories:
            logger.warning(f"categoria {category} no existe, usando 'win' por defecto")
            category = "win"
        
        # si ya esta cacheado, devuelve uno random
        if category in self.cache and self.cache[category]:
            return random.choice(self.cache[category])
        
        # si no, busca en tenor
        try:
            search_term = random.choice(self.categories[category])
            session = await self._get_session()
            
            params = {
                "q": search_term,
                "key": self.api_key,
                "client_key": "discord_economy_bot",
                "limit": 20,
                "media_filter": "gif",
                "ar_range": "wide"
            }
            
            async with session.get(self.api_url, params=params, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("results"):
                        # guarda los urls en cache
                        gif_urls = [
                            result["media_formats"]["gif"]["url"]
                            for result in data["results"]
                            if "media_formats" in result and "gif" in result["media_formats"]
                        ]
                        
                        if gif_urls:
                            self.cache[category] = gif_urls
                            return random.choice(gif_urls)
                
        except asyncio.TimeoutError:
            logger.warning(f"timeout buscando gif de {category}")
        except Exception as e:
            logger.error(f"error buscando gif: {e}")
        
        # si todo falla, devuelve None
        return None
    
    def get_fallback_emoji(self, category: str) -> str:
        """
        devuelve un emoji si no hay gif
        porque a veces tenor no funciona o algo
        """
        emoji_map = {
            "money": "💰",
            "work": "💼",
            "win": "🎉",
            "lose": "😢",
            "slots": "🎰",
            "dice": "🎲",
            "cards": "🃏",
            "roulette": "🎡",
            "jackpot": "💎",
            "broke": "💸",
            "robbery": "🔫",
            "police": "🚔",
            "escape": "🏃",
            "fight": "⚔️",
            "explosion": "💥",
            "victory": "🏆",
            "dragon": "🐉",
            "dungeon": "🏰",
            "treasure": "💎",
            "monster": "👹",
            "magic": "✨",
            "boss": "👑",
            "death": "💀",
            "levelup": "⬆️",
        }
        return emoji_map.get(category, "❓")

# instancia global para reutilizar
_tenor_instance: Optional[TenorCore] = None

def get_tenor() -> TenorCore:
    """devuelve la instancia global de tenor"""
    global _tenor_instance
    if _tenor_instance is None:
        _tenor_instance = TenorCore()
    return _tenor_instance
