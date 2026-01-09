"""
Comandos básicos de economía, facil de extender y mantener. Intentaré expandir esto en el futuro.
"""

from discord.ext import commands
import discord
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path
import logging

logger = logging.getLogger('EconomyBasic')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db
from bot.config import ECONOMY_CONFIG

class EconomyBasic(commands.Cog):
    """Comandos básicos de economía"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Sistema de ganancias por mensajes"""
        # Ignorar bots y comandos
        if message.author.bot or message.content.startswith('.'):
            return
        
        user_data = db.get_user(str(message.author.id))
        
        # Incrementar contador de mensajes totales
        total_messages = user_data.get('total_messages', 0) + 1
        user_data['total_messages'] = total_messages
        
        # Verificar si alcanzó un milestone
        milestone_interval = ECONOMY_CONFIG.get('milestone_interval', 100)
        milestone_reward = ECONOMY_CONFIG.get('milestone_reward', 1000)
        
        if total_messages % milestone_interval == 0:
            db.add_money(str(message.author.id), milestone_reward, "wallet")
            await message.channel.send(
                f"🎉 ¡Felicidades {message.author.mention}! Has alcanzado **{total_messages} mensajes** y ganaste **{milestone_reward:,} coins** de bonus!"
            )
            logger.info(f'{message.author} alcanzó milestone de {total_messages} mensajes y recibió {milestone_reward} coins')
        
        last_earn = user_data.get('last_message_earn')
        
        # Cooldown de 60 segundos entre ganancias
        if last_earn:
            last_time = datetime.fromisoformat(last_earn)
            if datetime.now() - last_time < timedelta(seconds=ECONOMY_CONFIG['earning_cooldown']):
                return
        
        # Dar monedas por mensaje
        earn_amount = ECONOMY_CONFIG['earning_per_message']
        db.add_money(str(message.author.id), earn_amount, "wallet")
        user_data['last_message_earn'] = datetime.now().isoformat()
        db.update_user(str(message.author.id), user_data)

    @commands.command(name="daily", aliases=["d", "diario"])
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """
        Reclama tu recompensa diaria
        
        Gana dinero gratis cada 24 horas.
        Mantén tu racha para bonos extras!
        """
        logger.debug(f'Comando .daily ejecutado por {ctx.author} (ID: {ctx.author.id}) en {ctx.guild.name if ctx.guild else "DM"}')
        
        user_data = db.get_user(str(ctx.author.id))
        base_reward = ECONOMY_CONFIG['daily_reward']
        
        # Calcular streak bonus
        last_daily = user_data.get('last_daily')
        streak = user_data.get('daily_streak', 0)
        
        logger.debug(f'Usuario {ctx.author.id}: last_daily={last_daily}, streak={streak}')
        
        if last_daily:
            last_time = datetime.fromisoformat(last_daily)
            time_diff = datetime.now() - last_time
            
            # Si reclamó ayer, aumentar streak
            if timedelta(hours=24) <= time_diff <= timedelta(hours=48):
                streak += 1
            # Si pasó más de 48h, resetear streak
            elif time_diff > timedelta(hours=48):
                streak = 1
        else:
            streak = 1
        
        streak_bonus = streak * 100
        final_reward = base_reward + streak_bonus
        
        logger.info(f'{ctx.author} reclamó daily: {final_reward} coins (base: {base_reward}, streak bonus: {streak_bonus}, streak: {streak})')
        
        # Actualizar datos
        db.add_money(str(ctx.author.id), final_reward, "wallet")
        user_data['last_daily'] = datetime.now().isoformat()
        user_data['daily_streak'] = streak
        db.update_user(str(ctx.author.id), user_data)
        
        # Mensaje bonito
        embed = discord.Embed(
            title="💎 Daily Reclamado!",
            description=f"{ctx.author.mention}, aquí está tu recompensa diaria!",
            color=discord.Color.gold()
        )
        embed.add_field(name=" Recompensa Base", value=f"${base_reward:,}", inline=True)
        embed.add_field(name=" Bonus Racha", value=f"${streak_bonus:,}", inline=True)
        embed.add_field(name=" Total", value=f"${final_reward:,}", inline=True)
        embed.add_field(name=" Racha Actual", value=f"{streak} días", inline=False)
        embed.set_footer(text="¡Vuelve mañana para mantener tu racha!")
        
        await ctx.send(embed=embed)

    @commands.command(name="work", aliases=["trabajar", "w"])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        """
        Trabaja para ganar dinero
        
        Elige un trabajo aleatorio y gana monedas.
        Cooldown: 1 hora
        """
        jobs = [
            {"name": "programador", "emoji": "💻", "min": 300, "max": 600},
            {"name": "diseñador", "emoji": "🎨", "min": 250, "max": 500},
            {"name": "repartidor", "emoji": "🚚", "min": 200, "max": 400},
            {"name": "chef", "emoji": "👨‍🍳", "min": 280, "max": 550},
            {"name": "streamer", "emoji": "🎮", "min": 350, "max": 700},
            {"name": "youtuber", "emoji": "📹", "min": 320, "max": 650},
        ]
        
        job = random.choice(jobs)
        earnings = random.randint(job['min'], job['max'])
        
        db.add_money(str(ctx.author.id), earnings, "wallet")
        
        messages = [
            f"Trabajaste duro como {job['name']} y ganaste **${earnings:,}**!",
            f"Tu jornada como {job['name']} fue exitosa! Ganaste **${earnings:,}**",
            f"Completaste tu turno como {job['name']}. Pago: **${earnings:,}**",
        ]
        
        embed = discord.Embed(
            title=f"{job['emoji']} Trabajo Completado",
            description=f"{ctx.author.mention}, {random.choice(messages)}",
            color=discord.Color.green()
        )
        embed.set_footer(text="Cooldown: 1 hora")
        
        await ctx.send(embed=embed)

    @commands.command(name="balance", aliases=["bal", "dinero", "money"])
    async def balance(self, ctx, member: discord.Member = None):
        """
        Muestra el balance de un usuario
        
        Ver tu dinero o el de otro usuario.
        Uso: .balance [@usuario]
        """
        target = member or ctx.author
        user_data = db.get_user(str(target.id))
        
        wallet = user_data.get('wallet', 0)
        bank = user_data.get('bank', 0)
        total = wallet + bank
        
        embed = discord.Embed(
            title=f"💰 Balance de {target.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name=" Wallet", value=f"${wallet:,}", inline=True)
        embed.add_field(name=" Bank", value=f"${bank:,}", inline=True)
        embed.add_field(name=" Total", value=f"${total:,}", inline=True)
        
        if target == ctx.author:
            embed.set_footer(text="¡Sigue ganando más!")
        
        await ctx.send(embed=embed)

    @commands.command(name="transfer", aliases=["enviar", "pay", "pagar"])
    async def transfer(self, ctx, member: discord.Member, amount: int):
        """
        Transfiere dinero a otro usuario
        
        Envía dinero desde tu wallet a otro usuario.
        Hay un 2% de impuesto en transferencias.
        
        Uso: .transfer @usuario <cantidad>
        """
        if member == ctx.author:
            await ctx.send("❌ No puedes transferirte dinero a ti mismo, no seas tonto...")
            return
        
        if member.bot:
            await ctx.send("❌ No puedes transferir dinero a un bot. ¡Los bots no necesitan dinero!")
            return
        
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0. ¿Intentando hacer trampa?")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        # Calcular impuesto
        tax = int(amount * ECONOMY_CONFIG['transfer_tax'])
        final_amount = amount - tax
        
        # Realizar transferencia
        if db.transfer_money(str(ctx.author.id), str(member.id), amount):
            embed = discord.Embed(
                title="💸 Transferencia Exitosa",
                description=f"{ctx.author.mention} → {member.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="💵 Monto Enviado", value=f"${amount:,}", inline=True)
            embed.add_field(name="🏛️ Impuesto (2%)", value=f"${tax:,}", inline=True)
            embed.add_field(name="✅ Recibido", value=f"${final_amount:,}", inline=True)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Error en la transferencia. Intenta de nuevo.")

    @commands.command(name="beg", aliases=["mendigar"])
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def beg(self, ctx):
        """
        Pide dinero
        
        Mendiga por monedas. A veces funciona, a veces no.
        Cooldown: 5 minutos
        """
        # 70% de probabilidad de éxito
        if random.random() < 0.7:
            amount = random.randint(5, 100)
            db.add_money(str(ctx.author.id), amount, "wallet")
            
            messages = [
                f"Un amable desconocido te dio **${amount:,}**!",
                f"Encontraste **${amount:,}** en el suelo!",
                f"Alguien sintió pena y te dio **${amount:,}**",
                f"¡Qué suerte! Ganaste **${amount:,}** mendigando",
            ]
            
            await ctx.send(f"🙏 {ctx.author.mention}, {random.choice(messages)}")
        else:
            messages = [
                "Nadie te hizo caso... 😢",
                "La gente te ignoró completamente...",
                "Mejor suerte la próxima vez...",
                "Todos pasaron de largo...",
            ]
            await ctx.send(f"😔 {ctx.author.mention}, {random.choice(messages)}")

    @commands.command(name="deposit", aliases=["dep", "depositar"])
    async def deposit(self, ctx, amount: str):
        """
        Deposita dinero en el banco
        
        Guarda tu dinero de forma segura.
        Usa 'all' para depositar todo.
        
        Uso: .deposit <cantidad|all>
        """
        user_data = db.get_user(str(ctx.author.id))
        wallet = user_data.get('wallet', 0)
        
        if amount.lower() == "all":
            amount = wallet
        else:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send("❌ Cantidad inválida. Usa un número o 'all'")
                return
        
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        if wallet < amount:
            await ctx.send(f"❌ No tienes suficiente dinero en tu wallet. Tienes: ${wallet:,}")
            return
        
        # Mover dinero de wallet a bank
        user_data['wallet'] -= amount
        user_data['bank'] = user_data.get('bank', 0) + amount
        db.update_user(str(ctx.author.id), user_data)
        
        embed = discord.Embed(
            title="🏦 Depósito Exitoso",
            description=f"{ctx.author.mention}, depositaste **${amount:,}** en el banco",
            color=discord.Color.green()
        )
        embed.add_field(name="💵 Nuevo Wallet", value=f"${user_data['wallet']:,}", inline=True)
        embed.add_field(name="🏦 Nuevo Bank", value=f"${user_data['bank']:,}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="withdraw", aliases=["wd", "retirar"])
    async def withdraw(self, ctx, amount: str):
        """
        Retira dinero del banco
        
        Saca tu dinero del banco.
        Usa 'all' para retirar todo.
        
        Uso: .withdraw <cantidad|all>
        """
        user_data = db.get_user(str(ctx.author.id))
        bank = user_data.get('bank', 0)
        
        if amount.lower() == "all":
            amount = bank
        else:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send("❌ Cantidad inválida. Usa un número o 'all'")
                return
        
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        if bank < amount:
            await ctx.send(f"❌ No tienes suficiente dinero en el banco. Tienes: ${bank:,}")
            return
        
        # Mover dinero de bank a wallet
        user_data['bank'] -= amount
        user_data['wallet'] = user_data.get('wallet', 0) + amount
        db.update_user(str(ctx.author.id), user_data)
        
        embed = discord.Embed(
            title="💵 Retiro Exitoso",
            description=f"{ctx.author.mention}, retiraste **${amount:,}** del banco",
            color=discord.Color.green()
        )
        embed.add_field(name="💵 Nuevo Wallet", value=f"${user_data['wallet']:,}", inline=True)
        embed.add_field(name="🏦 Nuevo Bank", value=f"${user_data['bank']:,}", inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyBasic(bot))