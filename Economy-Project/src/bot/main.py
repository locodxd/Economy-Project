import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
import sys
from pathlib import Path
import traceback

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger('EconomyBot')

# Asegurar que existe el directorio de logs
Path('logs').mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# con esto podes reducir la verbosidad de los logs de discord.py si quieres
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)
logging.getLogger('discord.client').setLevel(logging.INFO)

logger.info('='*60)
logger.info('INICIANDO BOT DE ECONOMÍA')
logger.info('='*60)

logger.debug('Cargando variables de entorno...')
load_dotenv()
logger.debug('Variables de entorno cargadas')

TOKEN = os.getenv('DISCORD_TOKEN')
logger.debug(f'Token encontrado: {"Si" if TOKEN else "No"}')

if not TOKEN:
    logger.error("ERROR CRÍTICO: No se encontró DISCORD_TOKEN en el archivo .env")
    logger.error(f"Directorio actual: {Path.cwd()}")
    logger.error(f"Archivo .env existe: {Path('.env').exists()}")
    logger.info("Ejecuta configurator.py para configurar el bot")
    sys.exit(1)

logger.info(f'Token cargado correctamente (longitud: {len(TOKEN)} caracteres)')

PREFIX = '.'
logger.info(f'Prefijo de comandos: {PREFIX}')

logger.debug('Importando configuración del bot...')
try:
    from bot.config import ALLOWED_SERVERS, COMMAND_CHANNELS
    logger.info('Configuración importada correctamente')
except Exception as e:
    logger.error(f'Error al importar configuración: {e}')
    logger.debug(traceback.format_exc())
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

async def load_cogs():
    cogs_path = Path(__file__).parent / 'cogs'
    logger.info(f'Buscando cogs en: {cogs_path.absolute()}')
    
    if not cogs_path.exists():
        logger.error(f'ERROR: Directorio de cogs no encontrado en {cogs_path}')
        return 0, 0
    
    loaded = 0
    failed = 0
    
    cog_files = [f for f in os.listdir(cogs_path) if f.endswith('.py') and not f.startswith('__')]
    logger.info(f'Encontrados {len(cog_files)} archivos de cogs')
    
    for filename in cog_files:
        cog_name = f'bot.cogs.{filename[:-3]}'
        try:
            logger.debug(f'Intentando cargar: {cog_name}')
            await bot.load_extension(cog_name)
            logger.info(f'✓ Cargado: {filename[:-3]}')
            loaded += 1
        except Exception as e:
            logger.error(f'✗ Error cargando {filename}: {e}')
            logger.debug(traceback.format_exc())
            failed += 1
    
    return loaded, failed

@bot.event
async def on_ready():
    logger.info('='*60)
    logger.info('BOT CONECTADO EXITOSAMENTE')
    logger.info('='*60)
    logger.info(f'Usuario: {bot.user} (ID: {bot.user.id})')
    logger.info(f'Prefijo: {PREFIX}')
    logger.info(f'Latencia: {round(bot.latency * 1000)}ms')
    
    # Información de servidores
    logger.info(f'Conectado a {len(bot.guilds)} servidor(es):')
    for guild in bot.guilds:
        logger.info(f'  - {guild.name} (ID: {guild.id}, Miembros: {guild.member_count})')
    
    # Cargar cogs
    logger.info('Cargando cogs...')
    loaded, failed = await load_cogs()
    logger.info(f'Resultado: {loaded} cargados | {failed} fallidos')
    
    if failed > 0:
        logger.warning(f'Hay {failed} cogs que fallaron al cargar')
    
    # Sincronizar slash commands
    logger.info('Sincronizando slash commands...')
    try:
        synced = await bot.tree.sync()
        logger.info(f'✓ Sincronizados {len(synced)} slash commands')
        for cmd in synced:
            logger.debug(f'  - /{cmd.name}')
    except Exception as e:
        logger.error(f'✗ Error sincronizando comandos: {e}')
        logger.debug(traceback.format_exc())
    
    # Establecer presencia
    try:
        await bot.change_presence(
            activity=discord.Game(name=f"{PREFIX}help | Sistema de Economía")
        )
        logger.info('Presencia del bot establecida')
    except Exception as e:
        logger.error(f'Error estableciendo presencia: {e}')
    
    logger.info('='*60)
    logger.info('BOT COMPLETAMENTE OPERATIVO')
    logger.info('='*60)

@bot.event
async def on_guild_join(guild):
    logger.info(f'Bot añadido al servidor: {guild.name} (ID: {guild.id})')
    logger.debug(f'Miembros: {guild.member_count}, Owner: {guild.owner}')
    
    if ALLOWED_SERVERS:
        logger.debug(f'Verificando servidor contra lista de permitidos...')
        logger.debug(f'Servidores permitidos: {ALLOWED_SERVERS}')
        logger.debug(f'ID del servidor actual: {str(guild.id)}')
        
        if str(guild.id) not in ALLOWED_SERVERS:
            logger.warning(f'SERVIDOR NO AUTORIZADO: {guild.name} ({guild.id})')
            logger.warning(f'no bro no vas a hackear el sistema de economia asi')
            
            try:
                channel = guild.system_channel or guild.text_channels[0] if guild.text_channels else None
                if channel:
                    logger.debug(f'Enviando mensaje de salida al canal: {channel.name}')
                    embed = discord.Embed(
                        title="Acceso No Autorizado",
                        description="Este bot SOLO funciona en servidores autorizados.",
                        color=discord.Color.red()
                    )
                    embed.add_field(
                        name="Error",
                        value="El servidor no está en la lista de servidores permitidos.",
                        inline=False
                    )
                    embed.add_field(
                        name="Solución",
                        value="Contacta al owner del bot para autorizar este servidor o de caso contrario para de intentar estupideces.",
                        inline=False
                    )
                    embed.set_footer(text=f"Server ID: {guild.id}")
                    await channel.send(embed=embed)
                    logger.info('Mensaje de salida enviado')
                else:
                    logger.warning('No se pudo encontrar un canal para enviar mensaje')
            except Exception as e:
                logger.error(f'Error al enviar mensaje de salida: {e}')
                logger.debug(traceback.format_exc())
            
            try:
                await guild.leave()
                logger.info(f'✓ Salida exitosa del servidor: {guild.name}')
            except Exception as e:
                logger.error(f'Error al salir del servidor: {e}')
        else:
            logger.info(f'✓ Servidor autorizado: {guild.name}')
    else:
        logger.info('Sin restricciones de servidor configuradas')

@bot.check
async def globally_block_non_authorized_servers(ctx):
    """Bloquea comandos en servidores no autorizados"""
    if not ctx.guild:
        logger.debug('Comando ejecutado en DM, permitido')
        return True
    
    logger.debug(f'Comando: {ctx.command.name} | Usuario: {ctx.author} | Servidor: {ctx.guild.name} | Canal: {ctx.channel.name}')
    
    # Verificar servidor autorizado
    if ALLOWED_SERVERS and str(ctx.guild.id) not in ALLOWED_SERVERS:
        logger.warning(f'Comando bloqueado: servidor no autorizado ({ctx.guild.id})')
        return False
    
    # Verificar canal autorizado
    if COMMAND_CHANNELS:
        server_channels = COMMAND_CHANNELS.get(str(ctx.guild.id), [])
        if server_channels:
            if str(ctx.channel.id) not in server_channels:
                logger.debug(f'Comando bloqueado: canal no autorizado ({ctx.channel.id})')
                await ctx.send("Este canal no está habilitado para comandos.")
                return False
            else:
                logger.debug('Canal autorizado, permitiendo comando')
    
    return True

@bot.event
async def on_command_error(ctx, error):
    """Manejo global de errores"""
    if isinstance(error, commands.CommandNotFound):
        logger.debug(f'Comando no encontrado: {ctx.message.content}')
        await ctx.send(f"Comando no encontrado. Usa `{PREFIX}help` para ver los comandos disponibles.")
    elif isinstance(error, commands.MissingPermissions):
        logger.warning(f'Permisos faltantes: {ctx.author} intentó usar {ctx.command}')
        await ctx.send("No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        logger.debug(f'Argumentos faltantes en {ctx.command}: {error}')
        await ctx.send(f"Faltan argumentos. Usa `{PREFIX}help {ctx.command}` para más información.")
    elif isinstance(error, commands.BadArgument):
        logger.debug(f'Argumento inválido en {ctx.command}: {error}')
        await ctx.send(f"Argumento inválido. Usa `{PREFIX}help {ctx.command}` para más información.")
    elif isinstance(error, commands.CommandOnCooldown):
        logger.debug(f'Cooldown para {ctx.author} en {ctx.command}: {error.retry_after:.1f}s')
        await ctx.send(f"Este comando está en cooldown. Intenta de nuevo en {error.retry_after:.1f}s")
    elif isinstance(error, commands.CheckFailure):
        logger.debug(f'Check falló para {ctx.command}: {error}')
    else:
        logger.error(f'ERROR NO MANEJADO en comando {ctx.command}: {type(error).__name__}: {error}')
        logger.error(f'Usuario: {ctx.author} | Servidor: {ctx.guild} | Canal: {ctx.channel}')
        logger.error(f'Mensaje completo: {ctx.message.content}')
        logger.debug(traceback.format_exc())
        await ctx.send(f"Ocurrió un error: {str(error)}")

if __name__ == '__main__':
    logger.info('='*60)
    logger.info('INICIANDO PROCESO DEL BOT')
    logger.info('='*60)
    
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Discord.py version: {discord.__version__}')
    logger.debug(f'Directorio de trabajo: {Path.cwd()}')
    
    try:
        logger.info('Conectando a Discord...')
        bot.run(TOKEN, log_handler=None)
    except KeyboardInterrupt:
        logger.info('='*60)
        logger.info('Bot detenido por el usuario (Ctrl+C)')
        logger.info('='*60)
    except discord.LoginFailure:
        logger.error('='*60)
        logger.error('ERROR CRÍTICO: Token de Discord inválido')
        logger.error('Verifica tu token en el archivo .env')
        logger.error('='*60)
    except Exception as e:
        logger.error('='*60)
        logger.error(f'ERROR FATAL: {type(e).__name__}: {e}')
        logger.error('='*60)
        logger.debug(traceback.format_exc())
        input('Presiona Enter para salir...')