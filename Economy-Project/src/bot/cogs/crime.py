"""
Comandos de crimen y actividades ilegales jejejejeje
"""

from discord.ext import commands
import discord
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db

class PoliceEncounterView(discord.ui.View):
    """botones pal encuentro con policia"""
    
    def __init__(self, ctx, stolen_amount, target_mention):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.stolen = stolen_amount
        self.target = target_mention
        self.responded = False
    
    @discord.ui.button(label="Correr", style=discord.ButtonStyle.primary)
    async def run_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu decision bro", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        # 60% chance de escapar
        if random.random() < 0.6:
            db.add_money(str(self.ctx.author.id), self.stolen, "wallet")
            embed = discord.Embed(
                title="Escapaste!",
                description=f"Corriste como un n- digo flash y te escapaste con ${self.stolen:,}",
                color=discord.Color.green()
            )
        else:
            fine = int(self.stolen * 1.5)
            db.remove_money(str(self.ctx.author.id), fine, "wallet")
            embed = discord.Embed(
                title="Te atraparon",
                description=f"No corriste lo suficientemente rapido. Multa: ${fine:,}",
                color=discord.Color.red()
            )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    @discord.ui.button(label="Enfrentarlos", style=discord.ButtonStyle.danger)
    async def fight_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu decision bro", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        # 30% chance de exito
        if random.random() < 0.3:
            bonus = int(self.stolen * 1.5)
            db.add_money(str(self.ctx.author.id), bonus, "wallet")
            embed = discord.Embed(
                title="Victoria epica",
                description=f"Los enfrentaste y ganaste! ${bonus:,} + respeto de la calle",
                color=discord.Color.gold()
            )
        else:
            fine = int(self.stolen * 2)
            db.remove_money(str(self.ctx.author.id), fine, "wallet")
            embed = discord.Embed(
                title="Mala idea",
                description=f"Te arrestaron y perdiste ${fine:,}. No era GTA pa",
                color=discord.Color.red()
            )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    @discord.ui.button(label="Hacerte el civil", style=discord.ButtonStyle.secondary)
    async def blend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu decision bro", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        # 50% chance de exito
        if random.random() < 0.5:
            db.add_money(str(self.ctx.author.id), self.stolen, "wallet")
            embed = discord.Embed(
                title="Acting 10/10",
                description=f"Te hiciste el inocente y funciono. Ganaste ${self.stolen:,}",
                color=discord.Color.green()
            )
        else:
            fine = self.stolen
            db.remove_money(str(self.ctx.author.id), fine, "wallet")
            embed = discord.Embed(
                title="Mal actor",
                description=f"No te creyeron nada. Multa: ${fine:,}",
                color=discord.Color.orange()
            )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    async def on_timeout(self):
        """Si no responde en 30s, pierde el dinero"""
        if not self.responded:
            fine = self.stolen
            db.remove_money(str(self.ctx.author.id), fine, "wallet")
            
            embed = discord.Embed(
                title="Te quedaste congelado",
                description=f"No hiciste nada y te atraparon. Perdiste ${fine:,}",
                color=discord.Color.red()
            )
            
            for item in self.children:
                item.disabled = True
            
            try:
                await self.message.edit(embed=embed, view=self)
            except:
                pass

class HeistDecisionView(discord.ui.View):
    """Vista para decisiones durante un heist"""
    
    def __init__(self, ctx, potential_loot, place_name):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.loot = potential_loot
        self.place = place_name
        self.responded = False
    
    @discord.ui.button(label="Seguir con el plan", style=discord.ButtonStyle.primary)
    async def stick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu heist bro, intenta conseguir tus propias cosas", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        # 70% exito si sigue el plan
        if random.random() < 0.7:
            db.add_money(str(self.ctx.author.id), self.loot, "wallet")
            embed = discord.Embed(
                title="Plan ejecutado",
                description=f"Seguiste el plan y funcó. Robaste ${self.loot:,}",
                color=discord.Color.green()
            )
        else:
            fine = random.randint(500, 1000)
            db.remove_money(str(self.ctx.author.id), fine, "wallet")
            embed = discord.Embed(
                title="El plan falló",
                description=f"Algo salio mal. Multa: ${fine:,}",
                color=discord.Color.red()
            )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    @discord.ui.button(label="Improvisar", style=discord.ButtonStyle.danger)
    async def improvise_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu heist", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        if random.random() < 0.4:
            bonus = int(self.loot * 1.8)
            db.add_money(str(self.ctx.author.id), bonus, "wallet")
            embed = discord.Embed(
                title="Improvisacion Rockstar",
                description=f"Tu plan B fue mejor que el A. Robaste ${bonus:,}",
                color=discord.Color.gold()
            )
        else:
            fine = random.randint(800, 1500)
            db.remove_money(str(self.ctx.author.id), fine, "wallet")
            embed = discord.Embed(
                title="Improvisacion nivel 0",
                description=f"Todo salio mal. Multa: ${fine:,}",
                color=discord.Color.red()
            )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    @discord.ui.button(label="Abortar", style=discord.ButtonStyle.secondary)
    async def abort_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No es tu heist", ephemeral=True)
            return
        
        if self.responded:
            return
        
        self.responded = True
        
        # pierdes poco dinero pero seguro
        loss = random.randint(200, 400)
        db.remove_money(str(self.ctx.author.id), loss, "wallet")
        
        embed = discord.Embed(
            title="Heist abortado",
            description=f"Decidiste no arriesgar. Perdiste ${loss:,} en preparacion",
            color=discord.Color.orange()
        )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    async def on_timeout(self):
        """Si no responde, aborta automaticamente"""
        if not self.responded:
            loss = 300
            db.remove_money(str(self.ctx.author.id), loss, "wallet")
            
            embed = discord.Embed(
                title="Tiempo agotado",
                description=f"Tardaste mucho en decidir, te pareces a mi mamá. Perdiste ${loss:,}",
                color=discord.Color.red()
            )
            
            for item in self.children:
                item.disabled = True
            
            try:
                await self.message.edit(embed=embed, view=self)
            except:
                pass

class Crime(commands.Cog):
    """Comandos de crimen y actividades ilegales"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="search", aliases=["buscar"])
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def search(self, ctx, location: str = None):
        locations = {
            "auto": {"min": 50, "max": 300, "name": "un auto"},
            "basura": {"min": 10, "max": 100, "name": "la basura"},
            "bolsillos": {"min": 20, "max": 150, "name": "tus bolsillos"},
            "casa": {"min": 100, "max": 400, "name": "tu casa"},
            "parque": {"min": 30, "max": 200, "name": "el parque"},
            "mall": {"min": 80, "max": 350, "name": "el mall"},
        }
        
        if not location or location.lower() not in locations:
            ctx.command.reset_cooldown(ctx)
            places = ", ".join(locations.keys())
            await ctx.send(f"especifica donde: {places}")
            return
        
        location = location.lower()
        place = locations[location]
        
        jackpot = random.random() < 0.08
        nothing = random.random() < 0.15 and not jackpot
        cops = random.random() < 0.1
        
        if cops and not jackpot:
            fine = random.randint(100, 300)
            db.remove_money(str(ctx.author.id), fine, "wallet")
            messages = [
                f"la policia te paro buscando en {place['name']}, multa ${fine:,}",
                f"guardias de seguridad te cacharon, pagas ${fine:,}",
                f"mal momento, policia cerca. multa ${fine:,}",
            ]
            await ctx.send(f"{ctx.author.mention}, {random.choice(messages)}")
            return
        
        if nothing:
            messages = [
                f"buscaste en {place['name']} pero nada",
                f"alguien ya busco ahi antes",
                f"perdiste el tiempo en {place['name']}",
            ]
            await ctx.send(f"{ctx.author.mention}, {random.choice(messages)}")
            return
        
        if jackpot:
            found = random.randint(place['max'], place['max'] * 3)
            messages = [
                f"wtf encontraste ${found:,} en {place['name']}",
                f"jackpot ${found:,} escondidos en {place['name']}",
                f"suerte del siglo, ${found:,} en {place['name']}",
            ]
        else:
            found = random.randint(place['min'], place['max'])
            messages = [
                f"encontraste ${found:,} en {place['name']}",
                f"habia ${found:,} tirados en {place['name']}",
                f"${found:,} escondidos en {place['name']}",
            ]
        
        db.add_money(str(ctx.author.id), found, "wallet")
        await ctx.send(f"{ctx.author.mention}, {random.choice(messages)}")
    
    @commands.command(name="rob", aliases=["robar"])
    async def rob(self, ctx, target: discord.Member = None):
        """
        Intenta robar a otro usuario
        
        Puedes robar hasta 30% de su wallet.
        Riesgo: Si fallas, pagas una multa!
        Cooldown: 30 minutos
        
        Uso: .rob @usuario
        """
        if not target:
            await ctx.send("❌ Debes mencionar a quien quieres robar. Uso: .rob @usuario")
            return
        
        if target.id == ctx.author.id:
            await ctx.send("❌ No puedes robarte a ti mismo, genio, idolo, titán...")
            return
        
        if target.bot:
            await ctx.send("❌ No puedes robar a un bot. Nice try")
            return
        
        target_data = db.get_user(str(target.id))
        target_wallet = target_data.get('wallet', 0)
        
        if target_wallet < 100:
            await ctx.send(f"❌ {target.mention} esta muy pobre para robarle. Tiene menos de $100")
            return
        
        # verificar que el ladron tenga dinero para la multa
        robber_data = db.get_user(str(ctx.author.id))
        robber_wallet = robber_data.get('wallet', 0)
        
        fine = min(500, int(target_wallet * 0.3))
        
        if robber_wallet < fine:
            await ctx.send(f"❌ Necesitas al menos ${fine:,} en tu wallet para intentar robar (para pagar la multa si fallas)")
            return
        
        success_chance = 0.40
        
        perfect_heist = random.random() < 0.05
        
        cops_nearby = random.random() < 0.08 and not perfect_heist
        
        if perfect_heist:
            success = True
        elif cops_nearby:
            success = False
        else:
            success = random.random() < success_chance
        
        if success:
            stolen = random.randint(int(target_wallet * 0.1), int(target_wallet * 0.3))
            
            police_event = random.random() < 0.25 and not perfect_heist
            
            if police_event:
                embed = discord.Embed(
                    title="Alerta!",
                    description=f"Robaste ${stolen:,} pero viene la policia!\nQue haces?",
                    color=discord.Color.orange()
                )
                
                view = PoliceEncounterView(ctx, stolen, target.mention)
                message = await ctx.send(embed=embed, view=view)
                view.message = message
            else:
                db.remove_money(str(target.id), stolen, "wallet")
                db.add_money(str(ctx.author.id), stolen, "wallet")
                
                embed = discord.Embed(
                    title=" Robo Exitoso",
                    description=f"{ctx.author.mention} le robo a {target.mention}!",
                    color=discord.Color.green()
                )
                embed.add_field(name="Cantidad robada", value=f"${stolen:,}", inline=True)
                
                if perfect_heist:
                    embed.set_footer(text="Robo perfecto! Sin testigos")
                else:
                    embed.set_footer(text="Nadie te vio... por ahora")
                
                # quitar el dinero de la victima aqui
                db.remove_money(str(target.id), stolen, "wallet")
                
                await ctx.send(embed=embed)
        else:
            db.remove_money(str(ctx.author.id), fine, "wallet")
            
            embed = discord.Embed(
                title="🚨 Robo Fallido",
                description=f"{ctx.author.mention} intento robar a {target.mention} pero fallo!",
                color=discord.Color.red()
            )
            embed.add_field(name="Multa pagada", value=f"${fine:,}", inline=True)
            
            if cops_nearby:
                embed.set_footer(text="Habia policias cerca. F")
            else:
                embed.set_footer(text="Te cacharon in fraganti")
            
            await ctx.send(embed=embed)
    
    @commands.command(name="wanted", aliases=["buscado"])
    async def wanted(self, ctx, member: discord.Member = None):
        """
        Ver el nivel de búsqueda de un usuario
        
        Sistema de wanted level (futuro)
        Por ahora muestra estadísticas básicas.
        """
        target = member or ctx.author
        user_data = db.get_user(str(target.id))
        
        # por ahora solo mostruestra info basica luego lo ampliaré con el otro commit
        
        embed = discord.Embed(
            title=f"👮 Estado Criminal de {target.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # info basica
        wallet = user_data.get('wallet', 0)
        bank = user_data.get('bank', 0)
        
        embed.add_field(name="💵 Wallet", value=f"${wallet:,}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"${bank:,}", inline=True)
        embed.add_field(name="⭐ Wanted Level", value="⭐ (Limpio)", inline=False)
        
        embed.set_footer(text="Sistema de wanted en desarrollo")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="heist", aliases=["atraco"])
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def heist(self, ctx):
        """
        Realiza un atraco grande
        
        Intenta atracar un lugar random.
        Alto riesgo, alta recompensa!
        Cooldown: 1 hora
        """
        user_data = db.get_user(str(ctx.author.id))
        wallet = user_data.get('wallet', 0)
        
        if wallet < 500:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("❌ Necesitas al menos $500 para planear un heist")
            return
        
        places = [
            {"name": "tienda de conveniencia", "emoji": "🏪", "min": 300, "max": 800, "success": 0.6},
            {"name": "joyería", "emoji": "💎", "min": 1000, "max": 3000, "success": 0.4},
            {"name": "banco pequeño", "emoji": "🏦", "min": 2000, "max": 5000, "success": 0.3},
            {"name": "camión blindado", "emoji": "🚛", "min": 3000, "max": 7000, "success": 0.25},
            {"name": "casino", "emoji": "🎰", "min": 5000, "max": 10000, "success": 0.2},
        ]
        
        target = random.choice(places)
        
        informant = random.random() < 0.07
        success_chance = target['success']
        if informant:
            success_chance += 0.2
        
        ambush = random.random() < 0.05
        
        decision_event = random.random() < 0.30 and not ambush
        
        if decision_event:
            loot = random.randint(target['min'], target['max'])
            
            embed = discord.Embed(
                title=f"{target['emoji']} Situacion complicada",
                description=f"Estas a punto de robar {target['name']}\nPero algo no se siente bien...\n\nQue haces?",
                color=discord.Color.orange()
            )
            embed.add_field(name="Botin potencial", value=f"${loot:,}", inline=False)
            
            view = HeistDecisionView(ctx, loot, target['name'])
            message = await ctx.send(embed=embed, view=view)
            view.message = message
            return
        
        if ambush:
            success = False
        else:
            success = random.random() < success_chance
        
        embed = discord.Embed(title=f"{target['emoji']} Heist")
        embed.add_field(name="Objetivo", value=target['name'], inline=False)
        
        if success:
            loot = random.randint(target['min'], target['max'])
            db.add_money(str(ctx.author.id), loot, "wallet")
            
            embed.color = discord.Color.green()
            embed.add_field(name=" Éxito!", value=f"Robaste ${loot:,}", inline=False)
            
            if informant:
                embed.set_footer(text="Un informante te ayudo. Nice")
            else:
                embed.set_footer(text="Atraco limpio")
        else:
            fine = random.randint(500, 1500)
            db.remove_money(str(ctx.author.id), fine, "wallet")
            
            embed.color = discord.Color.red()
            embed.add_field(name=" Fracaso", value=f"Multa: ${fine:,}", inline=False)
            
            if ambush:
                embed.set_footer(text="Era una trampa! Te emboscaron")
            else:
                embed.set_footer(text="Algo salió mal")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Crime(bot))
