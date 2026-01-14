from discord.ext import commands
import discord
import logging
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db
from bot.config import ECONOMY_CONFIG
from utils.tenor_core import get_tenor
from utils.event_system import maybe_trigger_event

class WalletFoundView(discord.ui.View):
    def __init__(self, ctx, wallet_amount, cog):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.amount = wallet_amount
        self.responded = False
        self.cog = cog
    
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
        self.cog._modificar_aura(self.ctx.author.id, 100, "wallet_return")
        
        embed = discord.Embed(
            title="Buen final",
            description=f"GOOD BOY, Devolviste la billetera. El dueño te recompenso con ${reward:,}\n✨ +100 AURA (ahora sos mas santo)",
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
            self.cog._modificar_aura(self.ctx.author.id, 50, "wallet_steal_success")
            embed = discord.Embed(
                title="Te la quedaste",
                description=f"Nadie te vio. Ganaste ${self.amount:,}\n👿 +50 AURA negativa (sos un ladron)",
                color=discord.Color.gold()
            )
        else:
            fine = int(self.amount * 0.8)
            db.remove_money(str(self.ctx.author.id), fine, "wallet")
            self.cog._modificar_aura(self.ctx.author.id, -500, "wallet_steal_caught")
            embed = discord.Embed(
                title="Te cacharon",
                description=f"El dueño te vio y llamo a la policia. Multa: ${fine:,}\n💀 -500 AURA (sos un delincuente)",
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
        
        bonus = int(self.amount * 0.7)
        db.add_money(str(self.ctx.author.id), bonus, "wallet")
        self.cog._modificar_aura(self.ctx.author.id, 150, "wallet_search_owner")
        
        embed = discord.Embed(
            title="Karma positivo",
            description=f"Buscaste al dueño y te recompenso con ${bonus:,} + respeto\n⭐ +150 AURA (sos un santo)",
            color=discord.Color.blue()
        )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    async def on_timeout(self):
        if not self.responded:
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
    def __init__(self, bot):
        self.bot = bot
    
    def _tiene_plata(self, user_id, cantidad):
        saldo = db.get_user(str(user_id)).get('wallet', 0)
        return saldo >= cantidad, saldo
    
    async def _agregar_gif(self, embed, categoria):
        try:
            gif_url = await get_tenor().get_gif(categoria)
            if gif_url:
                embed.set_image(url=gif_url)
        except:
            pass
    
    def _obtener_aura(self, user_id):
        user = db.get_user(str(user_id))
        return user.get('aura', 0)
    
    def _obtener_wanted(self, user_id):
        user = db.get_user(str(user_id))
        return user.get('wanted_level', 0)
    
    def _calcular_penalidad_wanted(self, wanted_level):
        if wanted_level == 0:
            return 1.0
        elif wanted_level < 5:
            return 0.95  # 5% menos
        elif wanted_level < 15:
            return 0.85  # 15% menos
        elif wanted_level < 30:
            return 0.70  # 30% menos
        else:
            return 0.50  # 50% menos si eres muy buscado
    
    def _modificar_aura(self, user_id, cantidad, razon=""):
        user = db.get_user(str(user_id))
        aura_actual = user.get('aura', 0)
        aura_nueva = aura_actual + cantidad
        user['aura'] = aura_nueva
        db.update_user(str(user_id), user)
        return aura_nueva
    
    def _calcular_impuesto_aura(self, monto_base, aura):
        impuesto_base = int(monto_base * ECONOMY_CONFIG.get('transfer_tax', 0.02))
        
        if aura < 0:
            penalidad = int(impuesto_base * abs(aura) * 0.01)
            impuesto_final = impuesto_base + min(penalidad, int(monto_base * 0.10)) 
        else:
            impuesto_final = impuesto_base
        
        return impuesto_final
    
    @commands.Cog.listener()
    async def on_message(self, message):
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
                f"🎉 {message.author.mention} llego a **{total_messages} mensajes** y gano **{milestone_reward:,} coins**!"
            )
        
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
        user_data = db.get_user(str(ctx.author.id))
        premio_base = ECONOMY_CONFIG['daily_reward']
        
        wanted = self._obtener_wanted(ctx.author.id)
        penalidad = self._calcular_penalidad_wanted(wanted)
        
        ultimo_daily = user_data.get('last_daily')
        racha = user_data.get('daily_streak', 0)
        
        if ultimo_daily:
            ultima_vez = datetime.fromisoformat(ultimo_daily)
            diff = datetime.now() - ultima_vez
            
            if timedelta(hours=24) <= diff <= timedelta(hours=48):
                racha += 1
            elif diff > timedelta(hours=48):
                racha = 1
        else:
            racha = 1
        
        bonus_racha = racha * 100
        premio_final = int((premio_base + bonus_racha) * penalidad)  # ← Aplica penalidad
        
        db.add_money(str(ctx.author.id), premio_final, "wallet")
        user_data['last_daily'] = datetime.now().isoformat()
        user_data['daily_streak'] = racha
        db.update_user(str(ctx.author.id), user_data)
        
        embed = discord.Embed(
            title="💰 Daily reclamado",
            description=f"aca esta tu recompensa diaria {ctx.author.mention}",
            color=0xffd700
        )
        embed.add_field(name="Base", value=f"${premio_base:,}", inline=True)
        embed.add_field(name="Bonus racha", value=f"${bonus_racha:,}", inline=True)
        embed.add_field(name="Total", value=f"${premio_final:,}", inline=True)
        embed.add_field(name="Racha", value=f"{racha} días", inline=False)
        
        if wanted > 0:
            embed.add_field(name="Penalización", value=f"Wanted {wanted}pts: -{int((1-penalidad)*100)}% de recompensa", inline=False)
        
        embed.set_footer(text="vuelve mañana para seguir la racha")
        await self._agregar_gif(embed, "money")
        await ctx.send(embed=embed)

    @commands.command(name="weekly", aliases=["semanal"])
    @commands.cooldown(1, 604800, commands.BucketType.user)
    async def weekly(self, ctx):
        user_data = db.get_user(str(ctx.author.id))
        premio_base = 5000
        
        wanted = self._obtener_wanted(ctx.author.id)
        penalidad = self._calcular_penalidad_wanted(wanted)
        
        bonus_random = random.randint(0, 2000)
        premio_final = int((premio_base + bonus_random) * penalidad)

        db.add_money(str(ctx.author.id), premio_final, "wallet")
        user_data['last_weekly'] = datetime.now().isoformat()
        db.update_user(str(ctx.author.id), user_data)
        
        embed = discord.Embed(
            title="💰 Weekly reclamado",
            description=f"pinta que tuviste suerte {ctx.author.mention}",
            color=0xffd700
        )
        embed.add_field(name="Base", value=f"${premio_base:,}", inline=True)
        embed.add_field(name="Bonus random", value=f"${bonus_random:,}", inline=True)
        embed.add_field(name="Total", value=f"${premio_final:,}", inline=True)
        
        if wanted > 0:
            embed.add_field(name="Penalización", value=f"Wanted {wanted}pts: -{int((1-penalidad)*100)}% de recompensa", inline=False)
        
        embed.set_footer(text="vuelve en 7 dias")
        await self._agregar_gif(embed, "money")
        await ctx.send(embed=embed)

    @commands.command(name="work", aliases=["trabajar", "w"])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        jobs = [
            {"name": "programador", "emoji": "💻", "min": 287, "max": 612},
            {"name": "diseñador", "emoji": "🎨", "min": 243, "max": 489},
            {"name": "repartidor", "emoji": "🚚", "min": 195, "max": 417},
            {"name": "chef", "emoji": "👨‍🍳", "min": 271, "max": 538},
            {"name": "streamer", "emoji": "🎮", "min": 362, "max": 691},
            {"name": "youtuber", "emoji": "📹", "min": 314, "max": 658},
        ]
        
        job = random.choice(jobs)
        event_roll = random.random()
        
        if event_roll < 0.02:
            fine = random.randint(50, 200)
            db.remove_money(str(ctx.author.id), fine, "wallet")
            embed = discord.Embed(
                title="Te despidieron",
                description=f"{ctx.author.mention}, llegaste tarde al trabajo de {job['name']}. Multa: ${fine:,}",
                color=discord.Color.red()
            )
            await self._agregar_gif(embed, "sad")
            await ctx.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
            return
        
        # si te toca esto F
        elif event_roll < 0.05:
            accident_cost = random.randint(100, 300)
            db.remove_money(str(ctx.author.id), accident_cost, "wallet")
            embed = discord.Embed(
                title="Accidente en el trabajo",
                description=f"{ctx.author.mention}, tuviste un accidente como {job['name']}. Gastos médicos: ${accident_cost:,}",
                color=discord.Color.orange()
            )
            await self._agregar_gif(embed, "sad")
            await ctx.send(embed=embed)
            ctx.command.reset_cooldown(ctx)
            return
        
        elif event_roll < 0.13:
            promotion_bonus = random.randint(job['max'], job['max'] * 2)
            db.add_money(str(ctx.author.id), promotion_bonus, "wallet")
            embed = discord.Embed(
                title="Promoción!",
                description=f"{ctx.author.mention}, tu jefe quedó impresionado! Bonus especial de ${promotion_bonus:,} como {job['name']}!",
                color=discord.Color.gold()
            )
            await self._agregar_gif(embed, "win")
            await ctx.send(embed=embed)
            return
        
        elif event_roll < 0.18:
            double_pay = random.randint(job['min'] * 2, job['max'] * 2)
            db.add_money(str(ctx.author.id), double_pay, "wallet")
            embed = discord.Embed(
                title="Dia de pago doble",
                description=f"{ctx.author.mention}, era dia de pago doble! Ganaste ${double_pay:,} como {job['name']}!",
                color=discord.Color.gold()
            )
            await self._agregar_gif(embed, "money")
            await ctx.send(embed=embed)
            return
        
        elif event_roll < 0.25:
            base_pay = random.randint(job['min'], job['max'])
            overtime = int(base_pay * 0.5)
            total = base_pay + overtime
            db.add_money(str(ctx.author.id), total, "wallet")
            embed = discord.Embed(
                title="Horas extras",
                description=f"{ctx.author.mention}, trabajaste horas extras como {job['name']}!\nBase: ${base_pay:,} + Extras: ${overtime:,} = ${total:,}",
                color=discord.Color.green()
            )
            await self._agregar_gif(embed, "work")
            await ctx.send(embed=embed)
            return
        
        elif event_roll < 0.35 and job['name'] in ['repartidor', 'chef']:
            base_pay = random.randint(job['min'], job['max'])
            tip = random.randint(50, 200)
            total = base_pay + tip
            db.add_money(str(ctx.author.id), total, "wallet")
            embed = discord.Embed(
                title="Propina generosa",
                description=f"{ctx.author.mention}, un cliente te dio ${tip:,} de propina! Total como {job['name']}: ${total:,}",
                color=discord.Color.green()
            )
            await self._agregar_gif(embed, "money")
            await ctx.send(embed=embed)
            return
        
        elif event_roll < 0.37:
            stolen = random.randint(80, 250)
            db.remove_money(str(ctx.author.id), stolen, "wallet")
            embed = discord.Embed(
                title="Te robaron",
                description=f"{ctx.author.mention}, alguien te robo ${stolen:,} del locker en el trabajo. Llama a RH",
                color=discord.Color.red()
            )
            await self._agregar_gif(embed, "sad")
            await ctx.send(embed=embed)
            return
        
        earnings = random.randint(job['min'], job['max'])
        
        wanted = self._obtener_wanted(ctx.author.id)
        penalidad = self._calcular_penalidad_wanted(wanted)
        earnings = int(earnings * penalidad)
        
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
        if wanted > 0:
            embed.add_field(name="Penalización", value=f"Wanted {wanted}pts: -{int((1-penalidad)*100)}% de recompensa", inline=False)
        embed.set_footer(text=footer_text)
        await self._agregar_gif(embed, "work")
        await ctx.send(embed=embed)

    @commands.command(name="balance", aliases=["bal", "dinero", "money"])
    async def balance(self, ctx, member: discord.Member = None):
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
        await self._agregar_gif(embed, "money")
        await ctx.send(embed=embed)

    @commands.command(name="transfer", aliases=["enviar", "pay", "pagar"])
    async def transfer(self, ctx, miembro: discord.Member, plata: int):
        if miembro == ctx.author:
            return await ctx.send("no podes enviarte plata a vos mismo lol")
        
        tiene_guita, saldo = self._tiene_plata(ctx.author.id, plata)
        if not tiene_guita:
            return await ctx.send(f"no tenes ni ${plata:,} (saldo: ${saldo:,})")
        if plata <= 0:
            return await ctx.send("anda a enviar plata de verdad")
        
        aura_user = self._obtener_aura(ctx.author.id)
        impuesto = self._calcular_impuesto_aura(plata, aura_user)
        plata_final = plata - impuesto
        
        # hay que agradecer que no es mas alto el %
        chance_asalto = 0.10
        if aura_user < -200:
            chance_asalto = 0.15  
        
        evento = await maybe_trigger_event(ctx, chance_asalto, ["Huir", "Pelear", "Llamar a la policia"])

        if evento:
            if evento == "Huir":
                if random.random() < 0.65:
                    exito = db.transfer_money(str(ctx.author.id), str(miembro.id), plata)
                    nota = "escapaste, sigue la transferencia"
                else:
                    robo = int(plata * random.uniform(0.4, 0.9))
                    db.remove_money(str(ctx.author.id), robo, "wallet")
                    return await ctx.send(f"te asaltaron y perdiste ${robo:,}")
            elif evento == "Pelear":
                if random.random() < 0.45:
                    exito = db.transfer_money(str(ctx.author.id), str(miembro.id), plata)
                    extra = int(plata * 0.10)
                    db.add_money(str(ctx.author.id), extra, "wallet")
                    nota = f"ganaste la pelea y recuperaste ${extra:,}"
                else:
                    robo = int(plata * random.uniform(0.3, 0.8))
                    db.remove_money(str(ctx.author.id), robo, "wallet")
                    return await ctx.send(f"perdiste la pelea y te robaron ${robo:,}")
            else:  # policia
                if random.random() < 0.70:
                    exito = db.transfer_money(str(ctx.author.id), str(miembro.id), plata)
                    compensacion = int(plata * 0.20)
                    db.add_money(str(ctx.author.id), compensacion, "wallet")
                    nota = f"la policia llego y te dieron ${compensacion:,}"
                else:
                    robo = int(plata * random.uniform(0.2, 0.6))
                    db.remove_money(str(ctx.author.id), robo, "wallet")
                    return await ctx.send(f"la policia llego tarde, perdiste ${robo:,}")
            
            if exito:
                embed = discord.Embed(title="✅ Transferencia OK", color=0x2ecc71)
                embed.description = f"{ctx.author.mention} → {miembro.mention}"
                embed.add_field(name="Enviaste", value=f"${plata:,}", inline=True)
                embed.add_field(name="Impuesto", value=f"${impuesto:,}", inline=True)
                embed.add_field(name="Recibió", value=f"${plata_final:,}", inline=True)
                if nota:
                    embed.add_field(name="Evento", value=nota, inline=False)
                await ctx.send(embed=embed)
                # evento ultra raro: banco se equivoca (2%)
                if random.random() < 0.02:
                    regalo = int(plata_final * 0.5)
                    db.add_money(str(miembro.id), regalo, "wallet")
                    try:
                        await self._agregar_gif(embed, 'money')
                    except Exception as e:
                        logger = logging.getLogger(__name__)
                        logger.exception("Error adding gif after bank bug event")
                    await ctx.send(f"el banco se equivoco y le dio ${regalo:,} extra a {miembro.mention}")
                return

        # transferencia normal 
        if db.transfer_money(str(ctx.author.id), str(miembro.id), plata):
            embed = discord.Embed(title="✅ Transferencia OK", color=0x2ecc71)
            embed.description = f"{ctx.author.mention} → {miembro.mention}"
            embed.add_field(name="Enviaste", value=f"${plata:,}", inline=True)
            embed.add_field(name="Impuesto", value=f"${impuesto:,}", inline=True)
            embed.add_field(name="Recibió", value=f"${plata_final:,}", inline=True)
            # lol bug del banco
            if random.random() < 0.02:
                regalo = int(plata_final * 0.5)
                db.add_money(str(miembro.id), regalo, "wallet")
                embed.add_field(name="Evento", value=f"el banco se equivoco y le dio ${regalo:,} extra", inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ error en la transferencia")

    @commands.command(name="beg", aliases=["mendigar"])
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def beg(self, ctx):
        wanted = self._obtener_wanted(ctx.author.id)
        if wanted > 20:
            embed = discord.Embed(
                title="No puedes mendigar",
                description=f"{ctx.author.mention}, eras muy buscado. Nadie va a ayudarte cuando estás en la lista de criminalidad {wanted}pts",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        aura_user = self._obtener_aura(ctx.author.id)
        
        fail_rate = 0.30
        if aura_user < -100:
            penalidad_aura = 0.05 * (abs(aura_user) / 100)
            fail_rate += penalidad_aura
            fail_rate = min(fail_rate, 0.75)
        
        if wanted > 0:
            fail_rate += (wanted * 0.02)
            fail_rate = min(fail_rate, 0.80)
        
        event_roll = random.random()
        
        if event_roll < fail_rate:
            razon_falla = random.choice([
                "nadie quiso darte plata",
                "te ignoraron todos",
                f"te ves sospechoso (aura: {aura_user})"
            ])
            return await ctx.send(f"Intentaste mendigar pero {razon_falla}")
        
        if event_roll < 0.03:
            user_data = db.get_user(str(ctx.author.id))
            wallet = user_data.get('wallet', 0)
            if wallet > 100:
                stolen = random.randint(50, min(500, wallet // 2))
                choice = await maybe_trigger_event(ctx, 1.0, ["Huir", "Pelear", "Llamar a la policia"])
                if not choice:
                    db.remove_money(str(ctx.author.id), stolen, "wallet")
                    await ctx.send(f"No respondiste a tiempo y te robaron ${stolen:,}.")
                    ctx.command.reset_cooldown(ctx)
                    return
                if choice == "Huir":
                    if random.random() < 0.6:
                        await ctx.send(f"Lograste escapar sin perder nada.")
                    else:
                        db.remove_money(str(ctx.author.id), stolen, "wallet")
                        await ctx.send(f"Mientras huías te robaron ${stolen:,}.")
                        ctx.command.reset_cooldown(ctx)
                        return
                elif choice == "Pelear":
                    if random.random() < 0.45:
                        bonus = int(stolen * 0.2)
                        db.add_money(str(ctx.author.id), bonus, "wallet")
                        await ctx.send(f"Ganaste la pelea y recuperaste algo. Te dieron ${bonus:,} de vuelta.")
                    else:
                        db.remove_money(str(ctx.author.id), stolen, "wallet")
                        await ctx.send(f"Perdiste la pelea y te robaron ${stolen:,}.")
                        ctx.command.reset_cooldown(ctx)
                        return
                else:
                    if random.random() < 0.7:
                        reward = int(stolen * 0.3)
                        db.add_money(str(ctx.author.id), reward, "wallet")
                        await ctx.send(f"La policía llegó y te compensaron con ${reward:,}.")
                    else:
                        db.remove_money(str(ctx.author.id), stolen, "wallet")
                        await ctx.send(f"La policía no llegó a tiempo. Te robaron ${stolen:,}.")
                        ctx.command.reset_cooldown(ctx)
                        return
            else:
                await ctx.send(f"No había suficiente para robar, se fueron.")
                ctx.command.reset_cooldown(ctx)
                return
        
        elif event_roll < 0.07:  
            wallet_amount = random.randint(200, 800)
            
            embed = discord.Embed(
                title="Encontraste una billetera!",
                description=f"Hay ${wallet_amount:,} adentro. Que haces?",
                color=discord.Color.gold()
            )
            gif = await get_tenor().get_gif('treasure')
            if gif:
                embed.set_image(url=gif)
            view = WalletFoundView(ctx, wallet_amount, self)
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
                embed = discord.Embed(
                    title="Tu dia de suerte",
                    description=f"{ctx.author.mention}, una persona super generosa te dio ${amount:,}!",
                    color=discord.Color.gold()
                )
                await self._agregar_gif(embed, "money")
                await ctx.send(embed=embed)
                return
            
            db.add_money(str(ctx.author.id), amount, "wallet")
            
            messages = [
                f"alguien te dio **${amount:,}**",
                f"encontraste **${amount:,}** en el suelo",
                f"una señora te dio **${amount:,}**"
            ]
            
            embed = discord.Embed(
                title="Mendiga exitoso",
                description=f"{ctx.author.mention}, {random.choice(messages)}",
                color=discord.Color.green()
            )
            await self._agregar_gif(embed, "money")
            await ctx.send(embed=embed)
        else:
            fail_event = random.random()
            
            if fail_event < 0.15:
                await ctx.send(f"🚫 {ctx.author.mention}, seguridad te echo del area. No puedes mendigar aqui")
            elif fail_event < 0.30:
                await ctx.send(f"📖 {ctx.author.mention}, alguien te dio un sermón de 10 minutos sobre conseguir trabajo. No money tho")
            else:
                messages = [
                    "nadie te hizo caso",
                    "todos pasaron de largo",
                    "te miraron raro"
                ]
                await ctx.send(f"😔 {ctx.author.mention}, {random.choice(messages)}")

    @commands.command(name="deposit", aliases=["dep", "depositar"])
    async def deposit(self, ctx, amount: str):
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
            await ctx.send(f" no tenes suficiente. Tienes: ${wallet:,}")
            return
        
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
            await ctx.send(f"❌ no tenes suficiente. Tienes: ${bank:,}")
            return
        
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
    
    @commands.command(name="aura", aliases=["karma", "reputacion"])
    async def aura(self, ctx, miembro: discord.Member = None):
        if miembro is None:
            miembro = ctx.author
        
        aura = self._obtener_aura(miembro.id)
        
        if aura >= 500:
            alignment = " SANTO"
            color = discord.Color.gold()
        elif aura >= 100:
            alignment = " Buena persona"
            color = discord.Color.green()
        elif aura > -100:
            alignment = " Neutral (lo de siempre)"
            color = discord.Color.greyple()
        elif aura >= -500:
            alignment = " Villano "
            color = discord.Color.red()
        else:
            alignment = " DEMONIO "
            color = discord.Color.darker_red()
        
        embed = discord.Embed(
            title=f"AURA de {miembro.name}",
            description=f"Puntos de Reputación: {aura}",
            color=color
        )
        embed.add_field(name="Alignment", value=alignment, inline=False)
        
        if aura > 500:
            beneficio = f" Sos tan buena gente que los NPC quieren tu amistad"
        elif aura > 0:
            beneficio = f" Impuestos reducidos en transfers (-{int(10 * (aura / 1000))}%)"
        elif aura < -500:
            penalidad = f" Impuestos AUMENTADOS en transfers (+{int(10 * (abs(aura) / 500))}%)\nLiteralmente nadie confía en vos"
            beneficio = penalidad
        elif aura < 0:
            penalidad = f" Impuestos aumentados en transfers (+{int(10 * (abs(aura) / 500))}%)"
            beneficio = penalidad
        else:
            beneficio = " Neutral en todo"
        
        embed.add_field(name="Efecto Actual", value=beneficio, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="lawyer", aliases=["abogado"])
    @commands.cooldown(1, 21600, commands.BucketType.user)
    async def lawyer(self, ctx):
        wanted = self._obtener_wanted(ctx.author.id)
        
        if wanted == 0:
            await ctx.send(f"No necesitas abogado {ctx.author.mention}, no tenes wanted level")
            ctx.command.reset_cooldown(ctx)
            return
        
        costo = 500 + (wanted * 100)
        user_data = db.get_user(str(ctx.author.id))
        wallet = user_data.get('wallet', 0)
        
        if wallet < costo:
            embed = discord.Embed(
                title="No te alcanza la guita bro",
                description=f"{ctx.author.mention}, el abogado cobra ${costo:,} y vos tenes ${wallet:,}",
                color=discord.Color.red()
            )
            ctx.command.reset_cooldown(ctx)
            await ctx.send(embed=embed)
            return
        reduccion = random.randint(2, 5)
        nuevo_wanted = max(0, wanted - reduccion)
        
        db.remove_money(str(ctx.author.id), costo, "wallet")
        
        user_data['wanted_level'] = nuevo_wanted
        db.update_user(str(ctx.author.id), user_data)
        
        embed = discord.Embed(
            title="⚖️ Negociación Legal",
            description=f"{ctx.author.mention}, tu abogado negoció con la policía",
            color=discord.Color.blue()
        )
        embed.add_field(name="Costo", value=f"${costo:,}", inline=True)
        embed.add_field(name="Wanted Anterior", value=f"{wanted}pts", inline=True)
        embed.add_field(name="Wanted Nuevo", value=f"{nuevo_wanted}pts", inline=True)
        embed.add_field(name="Reducción", value=f"-{reduccion}pts", inline=False)
        embed.set_footer(text="Vuelve en 6 horas")
        await self._agregar_gif(embed, "celebration")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyBasic(bot))