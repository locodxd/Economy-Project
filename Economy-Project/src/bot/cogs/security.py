"""
Sistema de seguridad avanzado para el bot 
detecta patrones de macro y payloads sospechosos con precisión
bloquea comandos automaticamente cuando detecta abuso
"""

import discord
import datetime
from discord.ext import commands
from bot.utils.auth import is_config_admin
import re
from discord.ext import tasks
import time
import asyncio
from collections import defaultdict, deque
import logging


logger = logging.getLogger('Security')

class SecuritySystem(commands.Cog):

    @tasks.loop(hours=24)
    async def borrar_datos_antiguos(self):
        current_time = time.time()
        to_remove = [uid for uid, history in self.command_history.items()
                     if history and (current_time - history[-1]['timestamp'] > 86400)]
        for uid in to_remove:
            del self.command_history[uid]
            if uid in self.user_warnings and self.user_warnings[uid] == 0:
                del self.user_warnings[uid]

    def __init__(self, bot):
        self.bot = bot
        self.command_history = defaultdict(lambda: deque(maxlen=15))
        self.user_warnings = defaultdict(int)
        self.suspicious_cooldown = {}
        self.last_block_message = {}
        self.blocked_users = set()
        self.bot.add_check(self.global_security_check)
        self.blocked_users = set()
        self.min_account_age_days = 2  
        self.alt_account_cooldown = 120  
        self.bad_patterns = [
            # MongoDB/NoSQL injection operators y patrones comunes
            # sacada de una lista de google, puedes ampliarla si quieres
            # tiene cosas de XSS y SQLi tambien pero no es su foco principal
            # esto pueden usarlo si es q quieren migrar a sql o algo en el futuro
            r'\$eq',
            r'\$where',
            r'\$ne',
            r'\$gt',
            r'\$gte',
            r'\$lt',
            r'\$lte',
            r'\$nin',
            r'\$in\s*:',
            r'\$or',
            r'\$and',
            r'\$not',
            r'\$nor',
            r'\$exists',
            r'\$type',
            r'\$mod',
            r'\$regex',
            r'\$text',
            r'\$elemMatch',
            r'\$size',
            r'\$all',
            r'\{\s*\$',
            r'\[\s*\$',
            r'__proto__',
            r'constructor\s*\[',
            r'prototype\s*\[',
            r'<script',
            r'</script>',
            r'javascript:',
            r'onerror\s*=',
            r'onload\s*=',
            r'onclick\s*=',
            r'<iframe',
            r'<object',
            r'<embed',
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'popen\s*\(',
            r'subprocess',
            r'os\.system',
            r'__import__',
            r'\|.*\|',
            r'&&',
            r'\|\|',
            r';.*rm\s',
            r';.*drop',
            r';.*delete',
            r'`.*`',
            r'\$\(.*\)',
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+.*\s+set',
            r'--\s*$',
            r'/\*.*\*/',
            r"'\s+or\s+'1'\s*=\s*'1",
            r'"\s+or\s+"1"\s*=\s*"1',
            r'\.\./\.\.',
            r'\.\.\\\.\.', 
            r'\\x',
            r'\\u00',
            r'%00',
            r'null\s*byte',
        ]
        
        # parametros de deteccion estrictos pq el anterior dejaba spammear mucho y no servia casi de nd
        # puedes modificarlo a tu voluntad pero ten en cuenta que valores muy bajos pueden bloquear usuarios legitimos 
        # especialmente en servidores grandes con muchos comandos xd
        self.macro_threshold = 0.90  
        self.min_commands_check = 4  
        self.rapid_fire_window = 2.0  
        self.rapid_fire_limit = 4  
    
    def checkear_payload(self, text):
        if not text or not isinstance(text, str):
            return True
        
        text_lower = text.lower()
        
        for pattern in self.bad_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f'Patron sospechoso detectado: {pattern} en texto: {text[:50]}')
                return False
        
        special_chars = len(re.findall(r'[^\w\s]', text))
        if len(text) > 0 and special_chars / len(text) > 0.5:
            logger.warning(f'Demasiados caracteres especiales en: {text[:50]}')
            return False
        
        return True
    
    def es_una_alt_account(self, user):
        
        account_age = datetime.datetime.now(datetime.timezone.utc) - user.created_at
        account_age_days = account_age.days
        
        if account_age_days < self.min_account_age_days:
            logger.warning(f'Cuenta alt detectada: Usuario {user.id} con {account_age_days} días de antigüedad')
            return True
        
        return False
    
    def detect_rapid_fire(self, user_id):
        history = self.command_history[user_id]
        
        if len(history) < 3:
            return False
        
        current_time = time.time()
        recent_commands = [h for h in history if current_time - h['timestamp'] < self.rapid_fire_window]
        
        if len(recent_commands) >= self.rapid_fire_limit:
            logger.warning(f'Usuario {user_id} haciendo rapid fire: {len(recent_commands)} comandos en {self.rapid_fire_window}s')
            return True
        
        return False
    
    def detect_macro_pattern(self, user_id):
        history = self.command_history[user_id]
        
        if len(history) < self.min_commands_check:
            return False
        
        time_diffs = []
        for i in range(1, len(history)):
            time_diff = history[i]['timestamp'] - history[i-1]['timestamp']
            time_diffs.append(time_diff)
        
        if not time_diffs:
            return False
        
        avg = sum(time_diffs) / len(time_diffs)
        
        if avg < 1.5:
            logger.warning(f'Usuario {user_id} promedio de tiempo muy bajo: {avg:.2f}s')
            return True
        
        variance = sum((x - avg) ** 2 for x in time_diffs) / len(time_diffs)
        std_dev = variance ** 0.5
        
        if avg > 0:
            coefficient_of_variation = std_dev / avg
            
            if coefficient_of_variation < (1 - self.macro_threshold):
                commands_used = [h['command'] for h in history]
                unique_commands = len(set(commands_used))
                
                if unique_commands <= 2:
                    logger.warning(f'Usuario {user_id} posible macro: CV={coefficient_of_variation:.2f}, unicos={unique_commands}')
                    return True
        
        return False
    
    async def global_security_check(self, ctx):
        user_id = str(ctx.author.id)
        
        if user_id in self.blocked_users:
            current_time = time.time()
            if user_id in self.suspicious_cooldown:
                cooldown_end = self.suspicious_cooldown[user_id]
                if current_time < cooldown_end:
                    remaining = int(cooldown_end - current_time)
                    last_msg_time = self.last_block_message.get(user_id, 0)
                    if current_time - last_msg_time > 5:
                        await ctx.send(f'🚫 Estás bloqueado. {remaining}s restantes.')
                        self.last_block_message[user_id] = current_time
                    return False
                else:
                    self.blocked_users.remove(user_id)
                    del self.suspicious_cooldown[user_id]
                    self.user_warnings[user_id] = 0
        
        return True
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        
        user_id = str(ctx.author.id)
        current_time = time.time()
        
        if self.es_una_alt_account(ctx.author):
            self.user_warnings[user_id] += 1  # Solo 1 warning en vez de 2
            self.suspicious_cooldown[user_id] = current_time + self.alt_account_cooldown
            self.blocked_users.add(user_id)
            
            account_age_days = (discord.utils.utcnow() - ctx.author.created_at).days
            await ctx.send(f'⚠️ **Cuenta nueva** ({account_age_days} días). '
                          f'Debes esperar {self.min_account_age_days} días. '
                          f'Reintenta en {self.alt_account_cooldown // 60} minuto(s).')
            logger.warning(f'Cuenta nueva bloqueada: Usuario {user_id} con {account_age_days} días')
            return
        
        if not self.checkear_payload(ctx.message.content):
            self.user_warnings[user_id] += 3
            self.suspicious_cooldown[user_id] = current_time + 180
            self.blocked_users.add(user_id)
            
            await ctx.send(' Intento de inyección detectado. Bloqueado 3 minutos.')
            logger.critical(f'INTENTO DE INYECCIÓN de usuario {user_id}: {ctx.message.content[:100]}')
            return
        

        if self.detect_rapid_fire(user_id):
            self.user_warnings[user_id] += 2
            self.suspicious_cooldown[user_id] = current_time + 45
            self.blocked_users.add(user_id)
            await ctx.send(' Demasiados comandos muy rapido. Bloqueado 45s.')
            logger.warning(f'Usuario {user_id} bloqueado por rapid fire')
            return
        
        command_data = {
            'command': ctx.command.name if ctx.command else 'unknown',
            'timestamp': current_time
        }
        self.command_history[user_id].append(command_data)
        
        if len(self.command_history[user_id]) >= self.min_commands_check:
            if self.detect_macro_pattern(user_id):
                self.user_warnings[user_id] += 1
                
                if self.user_warnings[user_id] >= 2:
                    self.suspicious_cooldown[user_id] = current_time + 90
                    self.blocked_users.add(user_id)
                    await ctx.send(' Patrón de macro detectado. Bloqueado 90s.')
                    logger.warning(f'Usuario {user_id} bloqueado por patron de macro')
                    self.user_warnings[user_id] = 0
                else:
                    await ctx.send(' Tu patron de uso parece automatico. Ultimo aviso.')
                    logger.info(f'Usuario {user_id} primera advertencia de macro')
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        
        user_id = str(ctx.author.id)
        
        if user_id in self.blocked_users:
            return
        
        if isinstance(error, commands.BadArgument):
            
            if not self.check_payload(ctx.message.content):
                self.user_warnings[user_id] += 2
                
                current_time = time.time()
                self.suspicious_cooldown[user_id] = current_time + 120
                self.blocked_users.add(user_id)
                
                await ctx.send(' Payload sospechoso detectado. Bloqueado 2 minutos.')
                logger.warning(f'Payload bloqueado de usuario {user_id}: {ctx.message.content[:100]}')
    
    @commands.command(name='securitystatus')
    @is_config_admin()
    async def security_status(self, ctx):
        
        total_users_tracked = len(self.command_history)
        users_with_warnings = len([u for u, w in self.user_warnings.items() if w > 0])
        users_in_cooldown = len(self.suspicious_cooldown)
        
        embed = discord.Embed(
            title=' Sistema de Seguridad',
            color=discord.Color.red()
        )
        
        embed.add_field(name='Usuarios rastreados', value=str(total_users_tracked), inline=True)
        embed.add_field(name='Usuarios con warnings', value=str(users_with_warnings), inline=True)
        embed.add_field(name='Usuarios bloqueados', value=str(users_in_cooldown), inline=True)
        embed.add_field(
            name='Configuracion',
            value=f'Umbral macro: {self.macro_threshold}\nMin comandos: {self.min_commands_check}\nRapid fire: {self.rapid_fire_limit} cmds en {self.rapid_fire_window}s\nMin edad cuenta: {self.min_account_age_days} días',
            inline=False
        )
        
        if users_in_cooldown > 0:
            cooldown_list = []
            current_time = time.time()
            for user_id, end_time in list(self.suspicious_cooldown.items())[:5]:
                remaining = int(end_time - current_time)
                if remaining > 0:
                    cooldown_list.append(f'<@{user_id}>: {remaining}s')
            
            if cooldown_list:
                embed.add_field(
                    name='Usuarios en cooldown',
                    value='\n'.join(cooldown_list),
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clearwarnings')
    @is_config_admin()
    async def clear_warnings(self, ctx, user: discord.Member):
        
        user_id = str(user.id)
        
        if user_id in self.user_warnings:
            del self.user_warnings[user_id]
        
        if user_id in self.suspicious_cooldown:
            del self.suspicious_cooldown[user_id]
        
        if user_id in self.command_history:
            self.command_history[user_id].clear()

        await ctx.send(f'Warnings limpiados para {user.mention}')
        logger.info(f'Admin {ctx.author} limpio warnings de usuario {user_id}')

async def setup(bot):
    await bot.add_cog(SecuritySystem(bot))
