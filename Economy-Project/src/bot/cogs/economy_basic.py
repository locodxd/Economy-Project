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

class WalletFoundView(discord.ui.View):
    """Billetera encontrada"""
    
    def __init__(self, ctx, wallet_amount):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.amount = wallet_amount
        self.responded = False
    
    @discord.ui.button(label="Devolver la billetera", style=discord.ButtonStyle.success)
    async def return_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu billetera", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        reward = int(self.amount * 0.5)
        db.add_money(str(self.ctx.author.id), reward, "wallet")
        
        embed = discord.Embed(
            title="Buen final",
            description=f"GOOD BOY, Devolviste la billetera. El dueño te recompenso con ${reward:,}",
            color=discord.Color.green()
        )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    @discord.ui.button(label="Quedartela", style=discord.ButtonStyle.danger)
    async def keep_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu billetera", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        if random.random() < 0.7:
            db.add_money(str(self.ctx.author.id), self.amount, "wallet")
            embed = discord.Embed(
                title="Te la quedaste",
                description=f"Nadie te vio. Ganaste ${self.amount:,}",
                color=discord.Color.gold()
            )
        else:
            fine = int(self.amount * 0.8)
            db.remove_money(str(self.ctx.author.id), fine, "wallet")
            embed = discord.Embed(
                title="Te cacharon",
                description=f"El dueño te vio y llamo a la policia. Multa: ${fine:,}",
                color=discord.Color.red()
            )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    @discord.ui.button(label="Buscar al dueño", style=discord.ButtonStyle.primary)
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu billetera", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        # bonus por ser buena gente, no como el owner
        bonus = int(self.amount * 0.7)
        db.add_money(str(self.ctx.author.id), bonus, "wallet")
        
        embed = discord.Embed(
            title="Karma positivo",
            description=f"Buscaste al dueño y te recompenso con ${bonus:,} + respeto",
            color=discord.Color.blue()
        )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    async def on_timeout(self):
        """Si no responde, se queda congelado"""
        if not self.responded:
            # pierde la billetera por indeciso
            embed = discord.Embed(
                title="Demasiado lento",
                description="Mientras pensabas, alguien mas agarro la billetera y salió corriendo -1000 de aura",
                color=discord.Color.orange()
            )
            
            for item in self.children:
                item.disabled = True
            
            try:
                await self.message.edit(embed=embed, view=self)
            except:
                pass

class EconomyBasic(commands.Cog):
    """Comandos básicos de economía"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Sistema de ganancias por mensajes"""
        if message.author.bot or message.content.startswith('.'):
            return
        
        user_data = db.get_user(str(message.author.id))
        
        total_messages = user_data.get('total_messages', 0) + 1
        user_data['total_messages'] = total_messages
        
        milestone_interval = ECONOMY_CONFIG.get('milestone_interval', 100)
        milestone_reward = ECONOMY_CONFIG.get('milestone_reward', 1000)
        
        if total_messages % milestone_interval == 0:
            db.add_money(str(message.author.id), milestone_reward, "wallet")
            await message.channel.send(
                f"🎉 ¡Felicidades {message.author.mention}! Has alcanzado **{total_messages} mensajes** y ganaste **{milestone_reward:,} coins** de bonus!"
            )
            logger.info(f'{message.author} alcanzó milestone de {total_messages} mensajes y recibió {milestone_reward} coins')
        
        last_earn = user_data.get('last_message_earn')
        
        if last_earn:
            last_time = datetime.fromisoformat(last_earn)
            if datetime.now() - last_time < timedelta(seconds=ECONOMY_CONFIG['earning_cooldown']):
                return
        
        earn_amount = ECONOMY_CONFIG['earning_per_message']
        db.add_money(str(message.author.id), earn_amount, "wallet")
        user_data['last_message_earn'] = datetime.now().isoformat()
        db.update_user(str(message.author.id), user_data)

    @commands.command(name="daily", aliases=["d", "diario"])
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """
        Gana dinero gratis cada 24 horas.
        Mantén tu racha para bonos extras!
        """
        logger.debug(f'Comando .daily ejecutado por {ctx.author} (ID: {ctx.author.id}) en {ctx.guild.name if ctx.guild else "DM"}')
        
        bucket = self.daily._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        base_reward = ECONOMY_CONFIG['daily_reward']
        
        # esta mmd hace la racha
        last_daily = user_data.get('last_daily')
        streak = user_data.get('daily_streak', 0)
        
        logger.debug(f'Usuario {ctx.author.id}: last_daily={last_daily}, streak={streak}')
        
        if last_daily:
            last_time = datetime.fromisoformat(last_daily)
            time_diff = datetime.now() - last_time
            
            if timedelta(hours=24) <= time_diff <= timedelta(hours=48):
                streak += 1
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
            title=" Daily Reclamado!",
            description=f"{ctx.author.mention}, aquí está tu recompensa diaria!",
            color=discord.Color.gold()
        )
        embed.add_field(name=" Recompensa Base", value=f"${base_reward:,}", inline=True)
        embed.add_field(name=" Bonus Racha", value=f"${streak_bonus:,}", inline=True)
        embed.add_field(name=" Total", value=f"${final_reward:,}", inline=True)
        embed.add_field(name=" Racha Actual", value=f"{streak} días", inline=False)
        embed.set_footer(text="¡Vuelve mañana para mantener tu racha!")
        
        await ctx.send(embed=embed)

    @commands.command(name="weekly", aliases=["semanal"])
    @commands.cooldown(1, 604800, commands.BucketType.user)
    async def weekly(self, ctx):
        """
        Reclama tu recompensa semanal
        
        Gana una gran recompensa cada 7 días.
        Cooldown: 7 días
        """
        logger.debug(f'Comando .weekly ejecutado por {ctx.author} (ID: {ctx.author.id})')
        
        bucket = self.weekly._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        base_reward = 5000 
        
        bonus = random.randint(0, 2000)
        final_reward = base_reward + bonus
        
        logger.info(f'{ctx.author} reclamo weekly: {final_reward} coins (base: {base_reward}, bonus: {bonus})')

        db.add_money(str(ctx.author.id), final_reward, "wallet")
        user_data['last_weekly'] = datetime.now().isoformat()
        db.update_user(str(ctx.author.id), user_data)
        
        # Mensaje
        embed = discord.Embed(
            title=" Weekly Reclamado!",
            description=f"{ctx.author.mention}, aquí está tu recompensa semanal!",
            color=discord.Color.gold()
        )
        embed.add_field(name="💵 Recompensa Base", value=f"${base_reward:,}", inline=True)
        embed.add_field(name="🎁 Bonus Aleatorio", value=f"${bonus:,}", inline=True)
        embed.add_field(name="✨ Total", value=f"${final_reward:,}", inline=True)
        embed.set_footer(text="Vuelve en 7 días!")
        
        await ctx.send(embed=embed)

    @commands.command(name="work", aliases=["trabajar", "w"])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        """
        Trabaja para ganar dinero
        
        Elige un trabajo aleatorio y gana monedas.
        Cooldown: 1 hora
        """
        bucket = self.work._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        jobs = [
            {"name": "programador", "emoji": "💻", "min": 300, "max": 600},
            {"name": "diseñador", "emoji": "🎨", "min": 250, "max": 500},
            {"name": "repartidor", "emoji": "🚚", "min": 200, "max": 400},
            {"name": "chef", "emoji": "👨‍🍳", "min": 280, "max": 550},
            {"name": "streamer", "emoji": "🎮", "min": 350, "max": 700},
            {"name": "youtuber", "emoji": "📹", "min": 320, "max": 650},
        ]
        
        job = random.choice(jobs)
        event_roll = random.random()
        
        if event_roll < 0.02:
            fine = random.randint(50, 200)
            db.remove_money(str(ctx.author.id), fine, "wallet")
            await ctx.send(f"🚪 {ctx.author.mention}, te despidieron del trabajo de {job['name']} por llegar tarde. Multa: ${fine:,}")
            return
        
        # acá puede pasar cualquier cosa mala
        # evento: accidente en el trabajo u otra cosa
        elif event_roll < 0.05:
            accident_cost = random.randint(100, 300)
            db.remove_money(str(ctx.author.id), accident_cost, "wallet")
            await ctx.send(f"🤕 {ctx.author.mention}, tuviste un accidente como {job['name']}. Gastos médicos: ${accident_cost:,}")
            return
        
        elif event_roll < 0.13:
            promotion_bonus = random.randint(job['max'], job['max'] * 2)
            db.add_money(str(ctx.author.id), promotion_bonus, "wallet")
            await ctx.send(f"🎉 {ctx.author.mention}, tu jefe quedó impresionado! Bonus especial de ${promotion_bonus:,} como {job['name']}!")
            return
        
        elif event_roll < 0.18:
            double_pay = random.randint(job['min'] * 2, job['max'] * 2)
            db.add_money(str(ctx.author.id), double_pay, "wallet")
            await ctx.send(f"💰 {ctx.author.mention}, era dia de pago doble! Ganaste ${double_pay:,} como {job['name']}!")
            return
        
        elif event_roll < 0.25:
            base_pay = random.randint(job['min'], job['max'])
            overtime = int(base_pay * 0.5)
            total = base_pay + overtime
            db.add_money(str(ctx.author.id), total, "wallet")
            await ctx.send(f"⏰ {ctx.author.mention}, trabajaste horas extras como {job['name']}! Base: ${base_pay:,} + Extras: ${overtime:,} = ${total:,}")
            return
        
        elif event_roll < 0.35 and job['name'] in ['repartidor', 'chef']:
            base_pay = random.randint(job['min'], job['max'])
            tip = random.randint(50, 200)
            total = base_pay + tip
            db.add_money(str(ctx.author.id), total, "wallet")
            await ctx.send(f"💵 {ctx.author.mention}, un cliente te dio ${tip:,} de propina! Total como {job['name']}: ${total:,}")
            return
        
        elif event_roll < 0.37:
            stolen = random.randint(80, 250)
            db.remove_money(str(ctx.author.id), stolen, "wallet")
            await ctx.send(f"😡 {ctx.author.mention}, alguien te robo ${stolen:,} del locker en el trabajo. Llama a RH")
            return
        
        # trabajo normal
        earnings = random.randint(job['min'], job['max'])
        
        productive = random.random() < 0.15
        if productive:
            bonus = int(earnings * 0.3)
            earnings += bonus
            footer_text = f"Dia productivo! +${bonus:,} bonus"
        else:
            footer_text = "Cooldown: 1 hora"
        
        db.add_money(str(ctx.author.id), earnings, "wallet")
        
        messages = [
            f"Trabajaste duro como {job['name']} y ganaste **${earnings:,}**!",
            f"Tu jornada como {job['name']} fue exitosa! Ganaste **${earnings:,}**",
            f"Completaste tu turno como {job['name']}. Pago: **${earnings:,}**",
            f"Otro dia como {job['name']}, otro pago: **${earnings:,}**",
            f"Buen trabajo como {job['name']}! Ganaste **${earnings:,}**",
        ]
        
        embed = discord.Embed(
            title=f"{job['emoji']} Trabajo Completado",
            description=f"{ctx.author.mention}, {random.choice(messages)}",
            color=discord.Color.green()
        )
        embed.set_footer(text=footer_text)
        
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
            await ctx.send(" No puedes transferirte dinero a ti mismo, no seas tonto broder...")
            return
        
        if member.bot:
            await ctx.send(" No puedes transferir dinero a un bot. ¡Los bots no necesitan dinero!")
            return
        
        if amount <= 0:
            await ctx.send(" La cantidad debe ser mayor que 0. ¿Intentando hacer trampa?")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f" No tienes suficiente dinero como el creador del codigo. Tu wallet: ${user_data.get('wallet', 0):,}")
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
        bucket = self.beg._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        event_roll = random.random()
        
        if event_roll < 0.03:
            user_data = db.get_user(str(ctx.author.id))
            wallet = user_data.get('wallet', 0)
            if wallet > 100:
                stolen = random.randint(50, min(500, wallet // 2))
                db.remove_money(str(ctx.author.id), stolen, "wallet")
                await ctx.send(f"😨 {ctx.author.mention}, alguien te asaltó mientras mendigabas y te robó ${stolen:,}! F")
                return
            else:
                await ctx.send(f"😅 {ctx.author.mention}, intentaron asaltarte pero estas tan pobre que se fueron. Sad pero safe")
                return
        
        elif event_roll < 0.07:
            wallet_amount = random.randint(200, 800)
            
            embed = discord.Embed(
                title="Encontraste una billetera!",
                description=f"Hay ${wallet_amount:,} adentro. Que haces?",
                color=discord.Color.gold()
            )
            
            view = WalletFoundView(ctx, wallet_amount)
            message = await ctx.send(embed=embed, view=view)
            view.message = message
            return
        
        elif event_roll < 0.10:
            cop_help = random.randint(150, 400)
            db.add_money(str(ctx.author.id), cop_help, "wallet")
            await ctx.send(f"👮 {ctx.author.mention}, un policia vio tu situación y te dio ${cop_help:,}. Respect")
            return
        
        elif event_roll < 0.12:
            charity = random.randint(300, 700)
            db.add_money(str(ctx.author.id), charity, "wallet")
            await ctx.send(f"🏥 {ctx.author.mention}, una organización de caridad te dio ${charity:,} y un folleto de ayuda social")
            return
        
        elif event_roll < 0.17:
            tourist_money = random.randint(100, 500)
            db.add_money(str(ctx.author.id), tourist_money, "wallet")
            await ctx.send(f"🗽 {ctx.author.mention}, un turista no entendió la moneda local y te dio ${tourist_money:,}! Stonks")
            return
        
        elif event_roll < 0.20:
            tip_money = random.randint(20, 80)
            db.add_money(str(ctx.author.id), tip_money, "wallet")
            await ctx.send(f"🎭 {ctx.author.mention}, otro mendigo profesional te enseño sus trucos y te dio ${tip_money:,} para empezar")
            return
        
        if random.random() < 0.7:
            amount = random.randint(5, 100)
            
            if random.random() < 0.12:
                amount = random.randint(150, 300)
                db.add_money(str(ctx.author.id), amount, "wallet")
                await ctx.send(f"💝 {ctx.author.mention}, una persona super generosa te dio ${amount:,}! Tu dia de suerte")
                return
            
            db.add_money(str(ctx.author.id), amount, "wallet")
            
            messages = [
                f"Un amable desconocido te dio **${amount:,}**!",
                f"Encontraste **${amount:,}** en el suelo!",
                f"Alguien sintió pena y te dio **${amount:,}**",
                f"¡Qué suerte! Ganaste **${amount:,}** mendigando",
                f"Una señora te dio **${amount:,}** y una bendición",
                f"Un niño compartió su mesada contigo: **${amount:,}**",
            ]
            
            await ctx.send(f"🙏 {ctx.author.mention}, {random.choice(messages)}")
        else:
            fail_event = random.random()
            
            if fail_event < 0.15:
                await ctx.send(f"🚫 {ctx.author.mention}, seguridad te echo del area. No puedes mendigar aqui")
            elif fail_event < 0.30:
                await ctx.send(f"📖 {ctx.author.mention}, alguien te dio un sermón de 10 minutos sobre conseguir trabajo. No money tho")
            else:
                # mensajes de fracaso como el que creó el codigo, mentira, soy el mejor
                messages = [
                    "Nadie te hizo caso... ",
                    "La gente te ignoró completamente...",
                    "Mejor suerte la próxima vez...",
                    "Todos pasaron de largo...",
                    "Fingieron que no existias...",
                    "Te miraron raro y se fueron...",
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
                await ctx.send(" Cantidad inválida. Usa un número o 'all'")
                return
        
        if amount <= 0:
            await ctx.send(" La cantidad debe ser mayor que 0")
            return
        
        if wallet < amount:
            await ctx.send(f" No tienes suficiente dinero en tu wallet. Tienes: ${wallet:,}")
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