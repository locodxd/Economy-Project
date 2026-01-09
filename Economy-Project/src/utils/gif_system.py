from typing import Optional
import requests

class TenorGifSystem:
    API_KEY = 'YOUR_TENOR_API_KEY'  # Reemplaza esto por tu clave de API de Tenor puedes usarlo sin, pero es muy bonito tenerla
    BASE_URL = 'https://api.tenor.com/v1/search'

    @classmethod
    def get_gif(cls, query: str, limit: Optional[int] = 1) -> Optional[str]:
        params = {
            'q': query,
            'key': cls.API_KEY,
            'limit': limit,
            'media_filter': 'minimal'
        }
        response = requests.get(cls.BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                return data['results'][0]['media'][0]['gif']['url']
        return None

    @classmethod
    def get_random_gif(cls, category: str) -> Optional[str]:
        return cls.get_gif(category)