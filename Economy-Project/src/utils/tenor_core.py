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
        # soporta multiples keys para fallback (configuradas como TENOR_API_KEY_1, TENOR_API_KEY_2, etc)
        self.api_keys = []
        
        if api_key:
            self.api_keys.append(api_key)
        else:
            # buscar key principal
            main_key = os.getenv('TENOR_API_KEY')
            if main_key:
                self.api_keys.append(main_key)
            
            # buscar keys adicionales (TENOR_API_KEY_1, TENOR_API_KEY_2, etc)
            i = 1
            while True:
                extra_key = os.getenv(f'TENOR_API_KEY_{i}')
                if not extra_key:
                    break
                self.api_keys.append(extra_key)
                i += 1
        
        self.current_key_index = 0
        
        if not self.api_keys:
            logger.warning("no hay TENOR_API_KEY configurada, usando fallback de gifs")
            logger.warning("ejecuta configurator.py para configurar la api key de tenor")
        else:
            logger.info(f"tenor inicializado con {len(self.api_keys)} API key(s)")
        
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
        """crea session si no existe o si esta cerrada"""
        try:
            if self.session is None or self.session.closed:
                logger.debug("creando nueva sesion aiohttp para tenor")
                self.session = aiohttp.ClientSession()
        except Exception as e:
            logger.warning(f"error al crear sesion: {e}, intentando de nuevo")
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
        si no tiene api_key, usa fallback URLs
        """
        if category not in self.categories:
            logger.warning(f"categoria {category} no existe, usando 'win' por defecto")
            category = "win"
        
        # si ya esta cacheado, devuelve uno random
        if category in self.cache and self.cache[category]:
            return random.choice(self.cache[category])
        
        # si no tiene api key, usa fallback de imgur/giphy
        if not self.api_keys:
            logger.debug(f"sin API key, usando fallback para {category}")
            return self._get_fallback_gif(category)
        
        # intentar con cada api key disponible
        for attempt, api_key in enumerate(self.api_keys):
            try:
                search_term = random.choice(self.categories[category])
                session = await self._get_session()
                
                params = {
                    "q": search_term,
                    "key": api_key,
                    "client_key": "discord_economy_bot",
                    "limit": 20,
                    "media_filter": "gif",
                    "ar_range": "wide"
                }
                
                logger.debug(f"buscando gif tenor para: {search_term} (key #{attempt + 1})")
                
                async with session.get(self.api_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("results"):
                            # guarda los urls en cache
                            # prefer smaller gif formats when available
                            preferred = ["tinygif", "nanogif", "mediumgif", "gif"]
                            gif_urls = []
                            for result in data.get("results", []):
                                mf = result.get("media_formats", {})
                                for p in preferred:
                                    if p in mf and mf[p].get("url"):
                                        gif_urls.append(mf[p]["url"])
                                        break
                            
                            if gif_urls:
                                self.cache[category] = gif_urls
                                logger.debug(f"encontrado {len(gif_urls)} gifs para {category}")
                                return random.choice(gif_urls)
                            else:
                                logger.warning(f"no se encontraron formatos validos en tenor para {category}")
                        else:
                            logger.warning(f"tenor retorno vacio para {category}")
                    elif response.status == 429:
                        # rate limit, probar con la siguiente key
                        logger.warning(f"rate limit en tenor key #{attempt + 1}, intentando con siguiente")
                        continue
                    else:
                        logger.warning(f"tenor status {response.status} para {category}")
                    
            except asyncio.TimeoutError:
                logger.warning(f"timeout en key #{attempt + 1} buscando gif de {category}")
                continue
            except Exception as e:
                logger.error(f"error en key #{attempt + 1} buscando gif en tenor: {e}")
                continue
        
        # si todas las keys fallaron, usar fallback
        logger.info(f"todas las tenor keys fallaron para {category}, usando fallback")
        return self._get_fallback_gif(category)
    
    def _get_fallback_gif(self, category: str) -> Optional[str]:
        """
        devuelve gif fallback de imgur cuando no hay API key
        estos son urls publicos que funcionan sin autenticacion
        """
        fallback_gifs = {
            "money": "https://media.giphy.com/media/l0HlWy9x8FZo0XO1i/giphy.gif",
            "work": "https://media.giphy.com/media/l0HlJ6t7G7pnDsqkE/giphy.gif",
            "win": "https://media.giphy.com/media/g9GUusdUZsKFO/giphy.gif",
            "lose": "https://media.giphy.com/media/jjlR2z3MFBS3u8cUc3/giphy.gif",
            "slots": "https://media.giphy.com/media/l0HlOy9x8FZo0XO1i/giphy.gif",
            "dice": "https://media.giphy.com/media/l0HlN6Q7KZj5CdD8A/giphy.gif",
            "cards": "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
            "roulette": "https://media.giphy.com/media/kc8x1mVqjXe2gIODOL/giphy.gif",
            "jackpot": "https://media.giphy.com/media/ToMjGpKniGqjNvqTQm8/giphy.gif",
            "broke": "https://media.giphy.com/media/l3q2K5jinAlchEHqM/giphy.gif",
            "robbery": "https://media.giphy.com/media/3o7TKU2Nnq3iwN9A4o/giphy.gif",
            "police": "https://media.giphy.com/media/l0HlQjKvQZK2R2Lh6/giphy.gif",
            "escape": "https://media.giphy.com/media/l0HlVZkUUE5sDjDjG/giphy.gif",
            "fight": "https://media.giphy.com/media/l3q2K5jinAlchFH20/giphy.gif",
            "explosion": "https://media.giphy.com/media/3o6ZsYq8d6ve1Qt2bK/giphy.gif",
            "victory": "https://media.giphy.com/media/l0HlCXfcXJUg3z6dG/giphy.gif",
            "dragon": "https://media.giphy.com/media/l0HlDy9x8FZo0XO1i/giphy.gif",
            "dungeon": "https://media.giphy.com/media/l3q2K5jinAlchAhP6/giphy.gif",
            "treasure": "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
            "monster": "https://media.giphy.com/media/l0HlTy9x8FZo0XO1i/giphy.gif",
            "magic": "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
            "boss": "https://media.giphy.com/media/l3q2K5jinAlchEHqM/giphy.gif",
            "death": "https://media.giphy.com/media/xTiTnIHt8Aw7l0fLSM/giphy.gif",
            "levelup": "https://media.giphy.com/media/l0HlVZkUUE5sDjDjG/giphy.gif",
        }
        
        url = fallback_gifs.get(category)
        if url:
            logger.info(f"usando fallback gif para {category}")
        return url
    
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
