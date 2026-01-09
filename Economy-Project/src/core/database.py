"""
Sistema de base de datos JSON, porfavor valorar mi esfuerzo porque realmente me costó hacerlo :( para que no gasten dolares en una base de datos externa
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import shutil
import logging

logger = logging.getLogger('Database')

class JSONDatabase:
    
    def __init__(self, db_path: str = "database/users.json"):
        self.db_path = Path(db_path)
        logger.info(f'Inicializando base de datos en: {self.db_path.absolute()}')
        
        # Crear directorio si no existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f'Directorio de base de datos verificado: {self.db_path.parent.absolute()}')
        
        self.data = self._load()
        logger.info(f'Base de datos cargada: {len(self.data)} usuarios')
    
    def _load(self) -> Dict:
        if self.db_path.exists():
            try:
                logger.debug(f'Cargando datos desde {self.db_path}')
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f'Datos cargados correctamente: {len(data)} entradas')
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Archivo JSON corrupto: {e}")
                logger.warning("Creando backup del archivo corrupto y creando nuevo archivo")
                self._backup()
                return {}
            except Exception as e:
                logger.error(f"Error inesperado, asi como mi vida al cargar datos: {e}")
                return {}
        else:
            logger.warning(f'Archivo de base de datos no existe, se creará uno nuevo')
            return {}
    
    def _save(self):
        try:
            logger.debug(f'Guardando {len(self.data)} usuarios en base de datos')
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.debug('Datos guardados correctamente')
        except Exception as e:
            logger.error(f"Error guardando datos: {e}")
    
    def _backup(self):
        if self.db_path.exists():
            backup_dir = self.db_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}.json"
            
            try:
                shutil.copy(self.db_path, backup_path)
                logger.info(f"Backup creado: {backup_path}")
            except Exception as e:
                logger.error(f"Error creando backup: {e}")
    
    def get_user(self, user_id: str) -> Dict:
        user_id = str(user_id)
        if user_id not in self.data:
            logger.debug(f'Creando nuevo usuario: {user_id}')
            self.data[user_id] = self._create_default_user(user_id)
            self._save()
        return self.data[user_id]
    
    def _create_default_user(self, user_id: str) -> Dict:
        return {
            "user_id": user_id,
            "wallet": 0,
            "bank": 0,
            "inventory": {},
            "last_daily": None,
            "last_weekly": None,
            "last_work": None,
            "last_beg": None,
            "daily_streak": 0,
            "total_earned": 0,
            "total_spent": 0,
            "level": 1,
            "xp": 0,
            "created_at": datetime.now().isoformat(),
            "last_message_earn": None,
        }
    
    def update_user(self, user_id: str, data: Dict):
        user_id = str(user_id)
        if user_id not in self.data:
            self.data[user_id] = self._create_default_user(user_id)
        self.data[user_id].update(data)
        self._save()
    
    def add_money(self, user_id: str, amount: int, location: str = "wallet") -> bool:
        user = self.get_user(user_id)
        if location not in ["wallet", "bank"]:
            return False
        user[location] = user.get(location, 0) + amount
        user["total_earned"] = user.get("total_earned", 0) + amount
        self.update_user(user_id, user)
        return True
    
    def remove_money(self, user_id: str, amount: int, location: str = "wallet") -> bool:
        """Quita dinero del wallet o bank del usuario"""
        user = self.get_user(user_id)
        if location not in ["wallet", "bank"]:
            return False
        if user.get(location, 0) < amount:
            return False
        user[location] -= amount
        user["total_spent"] = user.get("total_spent", 0) + amount
        self.update_user(user_id, user)
        return True
    
    def transfer_money(self, from_id: str, to_id: str, amount: int) -> bool:
        from_user = self.get_user(from_id)
        if from_user.get("wallet", 0) < amount:
            return False
        
        if self.remove_money(from_id, amount, "wallet"):
            self.add_money(to_id, amount, "wallet")
            self._log_transaction(from_id, to_id, amount, "transfer")
            return True
        return False
    
    def _log_transaction(self, from_id: str, to_id: str, amount: int, trans_type: str):
        trans_path = self.db_path.parent / "transactions.json"
        transactions = []
        if trans_path.exists():
            with open(trans_path, 'r', encoding='utf-8') as f:
                transactions = json.load(f)
        
        transactions.append({
            "from": from_id,
            "to": to_id,
            "amount": amount,
            "type": trans_type,
            "timestamp": datetime.now().isoformat()
        })
        
        with open(trans_path, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, indent=2)
    
    def get_all_users(self) -> Dict:
        """Obtiene todos los usuarios de la base de datos"""
        return self.data
    
    def reset_user(self, user_id: str):
        """Resetea completamente un usuario a sus valores por defecto, esto lagea mucho asi q cuidado"""
        user_id = str(user_id)
        self.data[user_id] = self._create_default_user(user_id)
        self._save()
        logger.info(f"Usuario {user_id} reseteado")
    
    def set_user_data(self, user_id: str, wallet: int = None, bank: int = None):
        user_id = str(user_id)
        user = self.get_user(user_id)
        if wallet is not None:
            user["wallet"] = wallet
        if bank is not None:
            user["bank"] = bank
        self.update_user(user_id, user)
        logger.info(f"Datos actualizados para usuario {user_id}")

# Instancia global de la base de datos 
db = JSONDatabase()