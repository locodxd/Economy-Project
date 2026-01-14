# cancer de codigo pero funciona
import json
from pathlib import Path
import logging

logger = logging.getLogger('Config')

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
PREFIX = '.'

logger.info('Iniciando carga de configuración...')
BOT_CONFIG = {}
config_path = Path('config/bot_config.json')
logger.debug(f'Buscando archivo de configuración en: {config_path.absolute()}')

if config_path.exists():
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            BOT_CONFIG = json.load(f)
        logger.info('Configuración cargada exitosamente')
        logger.debug(f'Configuración: {BOT_CONFIG}')
    except json.JSONDecodeError as e:
        logger.error(f'Error al decodificar bot_config.json: {e}')
    except Exception as e:
        logger.error(f'Error inesperado al cargar configuración: {e}')
else:
    logger.warning(f'Archivo de configuración no encontrado en {config_path.absolute()}')
    logger.warning('Ejecuta configurator.py para crear la configuración')

ECONOMY_CONFIG = {
    "daily_reward": 1000,
    "weekly_reward": 10000,
    "transfer_tax": 0.02,
    "job_payment_range": {
        "min": 200,
        "max": 800
    },
    "gambling": {
        "min_bet": 10,
        "max_bet": 1000
    },
    "earning_per_message": 5,
    "earning_cooldown": 60,
    "milestone_reward": 1000, 
    "milestone_interval": 100,  
}

OWNER_ROLE = BOT_CONFIG.get('owner_role')
ADMIN_USER_IDS = BOT_CONFIG.get('admin_user_ids') or []
# Some configuraciones pueden estar presentes como `null` en el JSON. amigo esto es
# un dolor de orto
ALLOWED_SERVERS = BOT_CONFIG.get('allowed_servers') or []
COMMAND_CHANNELS = BOT_CONFIG.get('command_channels') or {}
MODO_PUBLICO = bool(BOT_CONFIG.get('modo_publico', False))
logger.info(f'Owner Role: {OWNER_ROLE if OWNER_ROLE else "No configurado"}')
logger.info(f'Admin Users: {len(ADMIN_USER_IDS)} usuario(s)')
logger.info(f'Servidores Permitidos: {len(ALLOWED_SERVERS)} servidor(es)')
logger.info(f'Canales Configurados: {len(COMMAND_CHANNELS)} servidor(es) con canales específicos')

if ALLOWED_SERVERS:
    logger.debug(f'Lista de servidores: {ALLOWED_SERVERS}')
if COMMAND_CHANNELS:
    logger.debug(f'Canales por servidor: {COMMAND_CHANNELS}')
DATA_DIR = "database"
USERS_DB = f"{DATA_DIR}/users.json"
SHOP_DB = f"{DATA_DIR}/shop_items.json"
TRANSACTIONS_DB = f"{DATA_DIR}/transactions.json"
logger.debug(f'Directorio de datos: {DATA_DIR}')