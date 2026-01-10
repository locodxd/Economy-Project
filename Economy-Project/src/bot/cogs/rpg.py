"""
rpg simple
basicamente haces misiones y peleas con cosas
"""

import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db
from utils.tenor_core import get_tenor
from utils.abilities import Abilities

class RPGStats:
    """aca van los stats de los jugadores en general"""
    
    @staticmethod
    def get_stats(user_id: str) -> dict:
        user_data = db.get_user(user_id)
        
        if 'rpg' not in user_data:
            user_data['rpg'] = {
                'level': 1,
                'xp': 0,
                'hp': 100,
                'max_hp': 100,
                'attack': 10,
                'defense': 5,
                'missions_done': 0,
                'bosses_killed': 0,
            }
            db.update_user(user_id, user_data)
        
        return user_data['rpg']
    
    @staticmethod
    def add_xp(user_id: str, xp: int) -> dict:
        stats = RPGStats.get_stats(user_id)
        stats['xp'] += xp
        
        xp_needed = stats['level'] * 100
        
        leveled_up = False
        if stats['xp'] >= xp_needed:
            stats['xp'] -= xp_needed
            stats['level'] += 1
            stats['max_hp'] += 20
            stats['hp'] = stats['max_hp']  
            stats['attack'] += 3
            stats['defense'] += 2
            leveled_up = True
        
        user_data = db.get_user(user_id)
        user_data['rpg'] = stats
        db.update_user(user_id, user_data)
        
        return {'leveled_up': leveled_up, 'new_level': stats['level']}
    
    @staticmethod
    def heal_user(user_id: str):
        stats = RPGStats
        stats['hp'] = stats['max_hp']

        user_data = db.get_user(user_id)
        user_data['rpg'] = stats
        db.update_user(user_id, user_data)
class MissionData:
    """aca van las misiones y bosses nomas"""
    
    MISSIONS = {
        'bandits': {
            'name': 'Pelear Bandidos',
            'desc': 'hay unos bandidos jodiendo en el pueblo, anda y pegales',
            'min_level': 1,
            'reward_money': 500,
            'reward_xp': 50,
        },
        'dragon': {
            'name': 'Matar Dragon',
            'desc': 'hay un dragon molestando, matalo y te pago',
            'min_level': 5,
            'reward_money': 3000,
            'reward_xp': 200,
        },
    }
    
    BOSSES = {
        'goblin': {
            'name': 'Rey Goblin',
            'desc': 'un goblin grande basicamente',
            'hp': 300,
            'attack': 20,
            'defense': 10,
            'min_level': 3,
            'reward_money': 2000,
            'reward_xp': 150,
        },
        'dragon': {
            'name': 'Dragon Rojo',
            'desc': 'un dragon que tira fuego y esas cosas',
            'hp': 800,
            'attack': 40,
            'defense': 20,
            'min_level': 8,
            'reward_money': 8000,
            'reward_xp': 500,
        },
    }

class CombatView(discord.ui.View):
    """botones para pelear nomas asi de una sencillo"""
    
    def __init__(self, ctx):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.action = None
    
    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.danger)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("no es tu pelea bro", ephemeral=True)
            return
        
        self.action = "attack"
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()
    
    @discord.ui.button(label="Defender", style=discord.ButtonStyle.primary)
    async def defend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("no es tu pelea bro", ephemeral=True)
            return
        
        self.action = "defend"
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()
    
    @discord.ui.button(label="Huir", style=discord.ButtonStyle.secondary)
    async def flee_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("no es tu pelea bro", ephemeral=True)
            return
        
        self.action = "flee"
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

class MissionDecisionView(discord.ui.View):
    """botones para decisiones en misiones"""
    
    def __init__(self, ctx, buttons_config: dict):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.buttons_config = buttons_config  # {'1': 'label1', '2': 'label2', '3': 'label3'} 
        self.choice = None
    
    @discord.ui.button(label="1️⃣", style=discord.ButtonStyle.primary, custom_id="choice_1")
    async def choice_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("no es tu mision bro", ephemeral=True)
            return
        self.choice = '1'
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()
    
    @discord.ui.button(label="2️⃣", style=discord.ButtonStyle.success, custom_id="choice_2")
    async def choice_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("no es tu mision bro", ephemeral=True)
            return
        self.choice = '2'
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()
    
    @discord.ui.button(label="3️⃣", style=discord.ButtonStyle.danger, custom_id="choice_3")
    async def choice_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("no es tu mision bro", ephemeral=True)
            return
        self.choice = '3'
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()

class RPG(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.tenor = get_tenor()
    
    @commands.group(name="rpg", invoke_without_command=True)
    async def rpg(self, ctx):
        """comandos rpg"""
        if ctx.invoked_subcommand is None:
            await ctx.send("usa `.rpg profile` o `.rpg missions` pa empezar")
    
    @rpg.command(name="profile", aliases=["stats"])
    async def profile(self, ctx):
        """mira tus stats"""
        stats = RPGStats.get_stats(str(ctx.author.id))
        user_data = db.get_user(str(ctx.author.id))
        
        # cuanta xp necesitas pa subir
        xp_needed = stats['level'] * 100
        
        embed = discord.Embed(
            title=f"{ctx.author.display_name} - Stats",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Level", value=f"{stats['level']}", inline=True)
        embed.add_field(name="XP", value=f"{stats['xp']}/{xp_needed}", inline=True)
        embed.add_field(name="HP", value=f"{stats['hp']}/{stats['max_hp']}", inline=True)
        embed.add_field(name="Ataque", value=f"{stats['attack']}", inline=True)
        embed.add_field(name="Defensa", value=f"{stats['defense']}", inline=True)
        embed.add_field(name="Guita", value=f"${user_data.get('wallet', 0):,}", inline=True)
        embed.add_field(name="Misiones", value=f"{stats['missions_done']}", inline=True)
        embed.add_field(name="Bosses", value=f"{stats['bosses_killed']}", inline=True)
        
        await ctx.send(embed=embed)
    
    @rpg.command(name="missions", aliases=["quests"])
    async def missions(self, ctx):
        """ve que misiones hay"""
        stats = RPGStats.get_stats(str(ctx.author.id))
        
        embed = discord.Embed(
            title="Misiones",
            description="usa `.rpg mission <id>` para hacerla",
            color=discord.Color.blue()
        )
        
        for mission_id, mission in MissionData.MISSIONS.items():
            puede = stats['level'] >= mission['min_level']
            status = "podes hacerla" if puede else f"necesitas level {mission['min_level']}"
            
            embed.add_field(
                name=f"{mission['name']} (ID: {mission_id})",
                value=f"{mission['desc']}\n"
                      f"Recompensa: ${mission['reward_money']:,} y {mission['reward_xp']} XP\n"
                      f"Status: {status}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @rpg.command(name="mission", aliases=["quest"])
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1 mision cada 60 segundos
    async def mission(self, ctx, mission_id: str = None):
        """hace una mision con decisiones"""
        if not mission_id:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("usa `.rpg mission <id>` o mira `.rpg missions`")
            return
        
        if mission_id not in MissionData.MISSIONS:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("esa mision no existe pa")
            return
        
        mission = MissionData.MISSIONS[mission_id]
        stats = RPGStats.get_stats(str(ctx.author.id))
        
        if stats['level'] < mission['min_level']:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"necesitas level {mission['min_level']}, sos level {stats['level']}")
            return
        
        if stats['hp'] <= 0:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("estas muerto amigo, usa `.rpg heal`")
            return
        
        # PRIMERA DECISIÓN
        embed1 = discord.Embed(
            title=f"{mission['name']}",
            description=mission['desc'],
            color=discord.Color.blue()
        )
        embed1.add_field(name="Tu HP", value=f"{stats['hp']}/{stats['max_hp']}", inline=False)
        embed1.add_field(name="1️⃣ Avanzar", value="ataque frontal directo", inline=False)
        embed1.add_field(name="2️⃣ Investigar", value="busca una ruta alternativa", inline=False)
        embed1.add_field(name="3️⃣ Retirarse", value="espera y observa", inline=False)
        embed1.set_footer(text="elige tu accion (30 segundos)")
        
        view1 = MissionDecisionView(ctx, {'1': 'Avanzar', '2': 'Investigar', '3': 'Retirarse'})
        msg1 = await ctx.send(embed=embed1, view=view1)
        await view1.wait()
        
        if view1.choice is None:
            ctx.command.reset_cooldown(ctx)
            await msg1.edit(content="se acabó el tiempo boludo", embed=None, view=None)
            return
        
        # Procesar primera decisión
        decision1_success = random.random() < 0.6  # 60%
        
        if view1.choice == '1':  # Avanzar
            if decision1_success:
                result1 = "avanzas directo sin problemas"
                damage1 = 0
            else:
                result1 = "¡emboscada! tomas daño"
                damage1 = random.randint(10, 20)
        
        elif view1.choice == '2':  # Investigar
            if decision1_success:
                result1 = "encuentras una ruta segura alternativa"
                damage1 = 0
            else:
                result1 = "¡trampa! caes y tomas daño"
                damage1 = random.randint(15, 25)
        
        else:  # Retirarse
            result1 = "esperas cautelosamente"
            damage1 = 0
        
        # Aplicar daño de primera decisión
        stats['hp'] = max(0, stats['hp'] - damage1)
        user_data = db.get_user(str(ctx.author.id))
        user_data['rpg'] = stats
        db.update_user(str(ctx.author.id), user_data)
        
        # Mostrar resultado
        embed_res1 = discord.Embed(description=result1, color=discord.Color.green() if damage1 == 0 else discord.Color.orange())
        if damage1 > 0:
            embed_res1.add_field(name="Daño", value=f"-{damage1} HP", inline=False)
        await msg1.edit(embed=embed_res1, view=None)
        await asyncio.sleep(2)
        
        if stats['hp'] <= 0:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("moriste en el intento")
            return
        
        # SEGUNDA DECISIÓN
        embed2 = discord.Embed(
            title="Encuentro Inesperado",
            description="ves un enemigo acercándose",
            color=discord.Color.red()
        )
        embed2.add_field(name="Tu HP", value=f"{stats['hp']}/{stats['max_hp']}", inline=False)
        embed2.add_field(name="1️⃣ Atacar", value="ataque sorpresa", inline=False)
        embed2.add_field(name="2️⃣ Distraer", value="intenta distraerlo", inline=False)
        embed2.add_field(name="3️⃣ Esconderse", value="busca un lugar seguro", inline=False)
        embed2.set_footer(text="elige tu accion (30 segundos)")
        
        view2 = MissionDecisionView(ctx, {'1': 'Atacar', '2': 'Distraer', '3': 'Esconderse'})
        msg2 = await ctx.send(embed=embed2, view=view2)
        await view2.wait()
        
        if view2.choice is None:
            ctx.command.reset_cooldown(ctx)
            await msg2.edit(content="se acabó el tiempo boludo", embed=None, view=None)
            return
        
        # Procesar segunda decisión
        decision2_success = random.random() < 0.5  # 50%
        xp_bonus = 0
        
        if view2.choice == '1':  # Atacar
            if decision2_success:
                result2 = "le pegaste directo, lo noqueas!"
                damage2 = 0
                xp_bonus = 30
            else:
                result2 = "¡falla! contraataca furioso"
                damage2 = random.randint(15, 30)
        
        elif view2.choice == '2':  # Distraer
            if decision2_success:
                result2 = "lo distraes y logras escapar"
                damage2 = 0
                xp_bonus = 15
            else:
                result2 = "no te cree y te persigue"
                damage2 = random.randint(10, 20)
        
        else:  # Esconderse
            if decision2_success:
                result2 = "te escondes perfectamente"
                damage2 = 0
                xp_bonus = 10
            else:
                result2 = "¡te encuentra! lucha desigual"
                damage2 = random.randint(20, 35)
        
        # Aplicar daño de segunda decisión
        damage2 = Abilities.apply_tank(str(ctx.author.id), damage2)
        stats['hp'] = max(0, stats['hp'] - damage2)
        user_data = db.get_user(str(ctx.author.id))
        user_data['rpg'] = stats
        db.update_user(str(ctx.author.id), user_data)
        
        # Mostrar resultado
        embed_res2 = discord.Embed(description=result2, color=discord.Color.green() if damage2 == 0 else discord.Color.orange())
        if damage2 > 0:
            embed_res2.add_field(name="Daño", value=f"-{damage2} HP", inline=False)
        await msg2.edit(embed=embed_res2, view=None)
        await asyncio.sleep(2)
        
        if stats['hp'] <= 0:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("moriste en el intento")
            return
        
        # RESULTADO FINAL
        total_damage = damage1 + damage2
        total_xp = mission['reward_xp'] + xp_bonus
        reward_money = Abilities.apply_luck(str(ctx.author.id), mission['reward_money'])
        
        db.add_money(str(ctx.author.id), reward_money, "wallet")
        level_up = RPGStats.add_xp(str(ctx.author.id), total_xp)
        
        stats = RPGStats.get_stats(str(ctx.author.id))
        stats['missions_done'] += 1
        user_data = db.get_user(str(ctx.author.id))
        user_data['rpg'] = stats
        db.update_user(str(ctx.author.id), user_data)
        
        final_embed = discord.Embed(
            title="Misión Completada!",
            description=f"completaste {mission['name']}",
            color=discord.Color.green()
        )
        final_embed.add_field(name="Dinero", value=f"${reward_money:,}", inline=True)
        final_embed.add_field(name="XP", value=f"+{total_xp}", inline=True)
        final_embed.add_field(name="Daño Total", value=f"-{total_damage} HP", inline=True)
        
        if level_up['leveled_up']:
            final_embed.add_field(name="Level Up!", value=f"subiste a level {level_up['new_level']}", inline=False)
        
        await ctx.send(embed=final_embed)
    
    @rpg.command(name="boss")
    @commands.cooldown(1, 120, commands.BucketType.user)  # 1 boss cada 2 minutos
    async def boss(self, ctx, boss_id: str = None):
        """pelea contra un boss"""
        if not boss_id:
            # mostrar bosses
            embed = discord.Embed(title="Bosses", color=discord.Color.red())
            
            for bid, boss in MissionData.BOSSES.items():
                embed.add_field(
                    name=f"{boss['name']} (ID: {bid})",
                    value=f"{boss['desc']}\n"
                          f"HP: {boss['hp']} | ATK: {boss['attack']} | DEF: {boss['defense']}\n"
                          f"Level minimo: {boss['min_level']}\n"
                          f"Premio: ${boss['reward_money']:,} y {boss['reward_xp']} XP",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            return
        
        if boss_id not in MissionData.BOSSES:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("ese boss no existe man")
            return
        
        boss = MissionData.BOSSES[boss_id]
        stats = RPGStats.get_stats(str(ctx.author.id))
        
        if stats['level'] < boss['min_level']:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"necesitas level {boss['min_level']} minimo")
            return
        
        if stats['hp'] <= 0:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("estas muerto bro")
            return
        
        # sistema de pelea por turnos
        boss_hp = boss['hp']
        player_hp = stats['hp']
        
        # mensaje inicial
        status = f"**Empieza la pelea contra {boss['name']}**\n\n{boss['name']} - HP: {boss_hp}/{boss['hp']}\nVos - HP: {player_hp}/{stats['max_hp']}"
        msg = await ctx.send(status)
        await asyncio.sleep(1)
        
        # pelea simple por turnos
        while boss_hp > 0 and player_hp > 0:
            
            # tu turno
            view = CombatView(ctx)
            status = f"**{boss['name']}** - HP: {boss_hp}/{boss['hp']}\n**Vos** - HP: {player_hp}/{stats['max_hp']}\n\nQue haces?"
            
            await msg.edit(content=status, view=view)
            await view.wait()
            
            if view.action == "flee":
                await msg.edit(content=f"te escapaste como un cobarde...\n\n{boss['name']} queda con {boss_hp} HP", view=None)
                return
            
            elif view.action == "attack":
                damage = stats['attack'] + random.randint(-3, 5)
                damage = max(1, damage - boss['defense'] // 3)
                
                critico = random.random() < Abilities.get_crit_chance(str(ctx.author.id))
                if critico:
                    damage = int(damage * 1.5)
                
                boss_hp -= damage
                
                action_msg = f"le pegaste {damage} de daño" + (" CRITICO" if critico else "")
                await msg.edit(content=f"{status}\n\n{action_msg}", view=view)
                
            elif view.action == "defend":
                await msg.edit(content=f"{status}\n\nte defendiste", view=view)
            
            if boss_hp <= 0:
                break
            
            await asyncio.sleep(1.5)
            
            # turno del boss
            boss_damage = boss['attack'] + random.randint(-3, 3)
            
            if view.action == "defend":
                boss_damage = max(1, boss_damage - stats['defense'] * 2)
            else:
                boss_damage = max(1, boss_damage - stats['defense'])
            
            boss_damage = Abilities.apply_tank(str(ctx.author.id), boss_damage)
            
            player_hp -= boss_damage
            
            # actualizar estado post-turno boss
            status = f"**{boss['name']}** - HP: {boss_hp}/{boss['hp']}\n**Vos** - HP: {player_hp}/{stats['max_hp']}\n\n{boss['name']} te pego {boss_damage} de daño"
            await msg.edit(content=status, view=None)
            await asyncio.sleep(1.5)
        
        # resultado
        if player_hp > 0:
            # ganaste
            db.add_money(str(ctx.author.id), boss['reward_money'], "wallet")
            level_up = RPGStats.add_xp(str(ctx.author.id), boss['reward_xp'])
            
            stats = RPGStats.get_stats(str(ctx.author.id))
            stats['hp'] = player_hp
            stats['bosses_killed'] += 1
            user_data = db.get_user(str(ctx.author.id))
            user_data['rpg'] = stats
            db.update_user(str(ctx.author.id), user_data)
            
            reward = Abilities.apply_luck(str(ctx.author.id), boss['reward_money'])
            result_msg = f"mataste a {boss['name']} papá\nganaste ${reward:,} y {boss['reward_xp']} XP"
            
            if level_up['leveled_up']:
                result_msg += f"\nsubiste a level {level_up['new_level']}"
            
            await msg.edit(content=result_msg, view=None)
        else:
            # perdiste
            stats = RPGStats.get_stats(str(ctx.author.id))
            stats['hp'] = 0
            user_data = db.get_user(str(ctx.author.id))
            user_data['rpg'] = stats
            db.update_user(str(ctx.author.id), user_data)
            
            await msg.edit(content=f"{boss['name']} te mato gg\nusa `.rpg heal` pa revivir (cuesta $500)", view=None)
    
    @rpg.command(name="heal")
    async def heal(self, ctx):
        """te cura o revive"""
        stats = RPGStats.get_stats(str(ctx.author.id))
        user_data = db.get_user(str(ctx.author.id))
        wallet = user_data.get('wallet', 0)
        
        if stats['hp'] >= stats['max_hp']:
            await ctx.send("ya tenes el hp lleno loco")
            return
        
        # cuesta mas si estas muerto
        cost = 500 if stats['hp'] <= 0 else 200
        
        if wallet < cost:
            await ctx.send(f"necesitas ${cost:,} pa curarte, tenes ${wallet:,}")
            return
        
        db.remove_money(str(ctx.author.id), cost, "wallet")
        RPGStats.heal(str(ctx.author.id))
        
        if stats['hp'] <= 0:
            await ctx.send(f"reviviste loco, te costo ${cost:,}")
        else:
            await ctx.send(f"te curaste, gastaste ${cost:,}")
    
    @rpg.command(name="abilities")
    async def abilities(self, ctx):
        abilities = Abilities.get_abilities(str(ctx.author.id))
        wallet = db.get_user(str(ctx.author.id)).get('wallet', 0)
        
        embed = discord.Embed(title="Habilidades", color=discord.Color.purple())
        
        for ability_id, ability in Abilities.ABILITIES.items():
            tiene = "tiene" if abilities[ability_id] else "no tiene"
            costo = ability['cost']
            embed.add_field(
                name=f"{ability['name']} - ${costo}",
                value=f"{ability['desc']}\n{tiene}",
                inline=False
            )
        
        embed.set_footer(text=f"Dinero: ${wallet:,} | usa .rpg buy_ability <id>")
        await ctx.send(embed=embed)
    
    @rpg.command(name="buy_ability")
    async def buy_ability(self, ctx, ability_id: str):
        result = Abilities.buy_ability(str(ctx.author.id), ability_id)
        
        if 'error' in result:
            await ctx.send(result['error'])
        else:
            await ctx.send(f"compraste {Abilities.ABILITIES[ability_id]['name']}")

async def setup(bot):
    await bot.add_cog(RPG(bot))
