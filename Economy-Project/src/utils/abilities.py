import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db
import random

class Abilities:
    
    ABILITIES = {
        'luck': {
            'name': 'Suerte',
            'desc': 'ganas 15% mas de dinero',
            'cost': 1500,
        },
        'grind': {
            'name': 'Molienda',
            'desc': 'cooldowns 20% mas rapido',
            'cost': 2000,
        },
        'crit': {
            'name': 'El Maestro de los criticos',
            'desc': 'critico 20% en lugar de 10%',
            'cost': 2500,
        },
        'tank': {
            'name': 'Tanque',
            'desc': 'recibis 20% menos de daño',
            'cost': 2000,
        },
    }
    
    @staticmethod
    def get_abilities(user_id: str):
        user = db.get_user(str(user_id))
        if 'abilities' not in user:
            user['abilities'] = {
                'luck': False,
                'grind': False,
                'crit': False,
                'tank': False,
            }
            db.update_user(str(user_id), user)
        return user['abilities']
    
    @staticmethod
    def buy_ability(user_id: str, ability_id: str):
        if ability_id not in Abilities.ABILITIES:
            return {'error': 'no existe esa habilidad'}
        
        user = db.get_user(str(user_id))
        abilities = user.get('abilities', {})
        wallet = user.get('wallet', 0)
        
        if abilities.get(ability_id, False):
            return {'error': 'ya tenes esa habilidad'}
        
        cost = Abilities.ABILITIES[ability_id]['cost']
        
        if wallet < cost:
            return {'error': f'necesitas ${cost:,}'}
        
        db.remove_money(str(user_id), cost, 'wallet')
        
        abilities[ability_id] = True
        user['abilities'] = abilities
        db.update_user(str(user_id), user)
        
        return {'success': True}
    
    @staticmethod
    def has_ability(user_id: str, ability_id: str):
        abilities = Abilities.get_abilities(user_id)
        return abilities.get(ability_id, False)
    
    @staticmethod
    def apply_luck(user_id: str, amount: int):
        if Abilities.has_ability(user_id, 'luck'):
            return int(amount * 1.15)
        return amount
    
    @staticmethod
    def apply_tank(user_id: str, damage: int):
        if Abilities.has_ability(user_id, 'tank'):
            return int(damage * 0.8)
        return damage
    
    @staticmethod
    def get_cooldown_reduction(user_id: str):
        if Abilities.has_ability(user_id, 'grind'):
            return 0.8  # 20% mas rapido
        return 1.0
    
    @staticmethod
    def get_crit_chance(user_id: str):
        chance = 0.1
        if Abilities.has_ability(user_id, 'crit'):
            chance = 0.2
        return chance
