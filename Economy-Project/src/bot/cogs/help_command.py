# sistema de ayuda personalizado, hecho por un pibe que no duerme

import discord
from discord.ext import commands
from typing import Optional
import logging

from bot.utils.auth import is_config_admin

logger = logging.getLogger(__name__)

class HelpView(discord.ui.View):
    
    def __init__(self, ctx, bot):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.bot = bot
        self.message = None
    
    @discord.ui.button(label="Home", style=discord.ButtonStyle.primary, custom_id="help_home")
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Eh, vos no sos el que puso el comando. No toques.", ephemeral=True)
            return
        
        embed = self.get_home_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Admin", style=discord.ButtonStyle.danger, custom_id="help_admin")
    async def admin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("No podes tocar esto si no sos vos el dueño del comando.", ephemeral=True)
            return
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("No tenes permisos de admin jefe, no te hagas el vivete.", ephemeral=True)
            return
        
        embed = self.get_admin_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="RPG", style=discord.ButtonStyle.success, custom_id="help_rpg")
    async def rpg_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("Eh, deja de tocar lo que no es tuyo.", ephemeral=True)
            return
        
        embed = self.get_rpg_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def get_home_embed(self):
        embed = discord.Embed(
            title="Sistema de Economia",
            description="Pone `.help <comando>` si queres ver que hace cada cosa",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="Basicos",
            value="\n".join([
                "`.daily` - Tu regalo diario",
                "`.weekly` - Tu regalo semanal",
                "`.work` - La famosa pala",
                "`.balance` - Cuanta plata tenes",
                "`.deposit` - Guardar en el banco",
                "`.withdraw` - Sacar del banco",
                "`.transfer` - Mandarle plata a alguien",
            ]),
            inline=True
        )
        
        embed.add_field(
            name="Ganar Guita",
            value="\n".join([
                "`.beg` - Mendigar un poco",
                "`.search` - Buscar algo por ahi",
                "`.rob` - Robarle a alguien (ojo)",
                "`.heist` - Un golpe grande",
            ]),
            inline=True
        )
        
        if self.bot.get_cog("Gambling"):
            embed.add_field(
                name="Casino",
                value="\n".join([
                    "`.coinflip` - Cara o cruz",
                    "`.dice` - Los daditos",
                    "`.slots` - Tragamonedas",
                    "`.blackjack` - El 21",
                    "`.roulette` - La ruleta",
                    "`.scratch` - Raspadita",
                    "`.crash` - El crash loco",
                ]),
                inline=True
            )
        
        embed.add_field(
            name="Tienda",
            value="\n".join([
                "`.tienda` - Ver que hay",
                "`.comprar` - Comprar algo",
                "`.inventario` - Tu bolso",
                "`.vender` - Vender tus cosas",
            ]),
            inline=True
        )
        
        embed.add_field(
            name="Extra",
            value="\n".join([
                "`.wanted` - Que tan buscado estas",
                "`.aura` - Ver tu aura",
                "`.leaderboard` - El top de los mejores",
            ]),
            inline=True
        )
        
        embed.add_field(
            name="Bonus",
            value="Si escribis mensajes vas ganando guita solo\nCada 100 mensajes te llevas un bonus de +1000",
            inline=False
        )
        
        embed.set_footer(text=f"Usa los botones para navegar | {len(self.bot.commands)} comandos")
        return embed
    
    def get_admin_embed(self):
        embed = discord.Embed(
            title="Comandos de Admin",
            description="Cosas privadas de los jefes.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Comandos",
            value="\n".join([
                "`/aeco_set` - Setear guita",
                "`/aeco_reset` - Resetear todo",
                "`/aeco_add` - Dar guita",
                "`/aeco_remove` - Quitar guita",
                "`/aeco_tienda` - Meter item a la tienda",
                "`/aeco_info` - Ver todo del user",
                "",
                "**Otras cosas:**",
                "`.setmilestone <cantidad>` - Cambiar premio milestone",
                "`.setinterval <num>` - Cambiar cada cuanto el premio",
            ]),
            inline=False
        )
        return embed
    
    def get_rpg_embed(self):
        embed = discord.Embed(
            title="Sistema RPG",
            description="Misiones, bosses y mejoras para el personaje",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Info",
            value="\n".join([
                "`.rpg profile` - Tus stats",
                "`.rpg missions` - Ver misiones",
            ]),
            inline=True
        )
        
        embed.add_field(
            name="Accion",
            value="\n".join([
                "`.rpg mission <id>` - Hacer una mision",
                "`.rpg boss <id>` - Ir contra un boss",
                "`.rpg heal` - Curarte (o revivir)",
            ]),
            inline=True
        )
        
        embed.add_field(
            name="Habilidades",
            value="\n".join([
                "`.rpg abilities` - Ver skills",
                "`.rpg buy_ability <id>` - Comprar skill",
            ]),
            inline=True
        )
        
        embed.add_field(
            name="Skills que podes tener",
            value="**luck** - +15% guita\n**grind** - Cooldowns mas rapidos\n**crit** - Golpes criticos\n**tank** - Aguantas mas golpes",
            inline=False
        )
        return embed
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception as e:
                logger.exception("Error editing help view message on timeout")

class HelpCommand(commands.Cog):
    # sistema de ayuda, no lo rompas porfa que costo un huevo XD
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help", aliases=["ayuda", "h"])
    async def help_command(self, ctx, comando: Optional[str] = None):
        if comando:
            cmd = self.bot.get_command(comando)
            if not cmd:
                return await ctx.send(f"No encontre el comando `{comando}` bro")
            embed = discord.Embed(
                title=f"Ayuda: {cmd.name}",
                description=cmd.help or "No tiene descripcion este comando",
                color=discord.Color.blue()
            )
            if cmd.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join(f"`{alias}`" for alias in cmd.aliases),
                    inline=False
                )
            
            usage = f".{cmd.name} {cmd.signature}" if cmd.signature else f".{cmd.name}"
            embed.add_field(name="Uso", value=f"`{usage}`", inline=False)
            await ctx.send(embed=embed)
        else:
            view = HelpView(ctx, self.bot)
            view.message = await ctx.send(embed=view.get_home_embed(), view=view)
    
    @commands.command(name="setmilestone")
    @is_config_admin()
    async def set_milestone_reward(self, ctx, cantidad: int):
        if cantidad < 0:
            await ctx.send("La guita tiene que ser positiva pa")
            return
        
        from bot.config import ECONOMY_CONFIG
        ECONOMY_CONFIG['milestone_reward'] = cantidad
        await ctx.send(f"Listo, ahora el premio por milestone es de **{cantidad:,} coins**")
    
    @commands.command(name="setinterval")
    @is_config_admin()
    async def set_milestone_interval(self, ctx, intervalo: int):
        if intervalo < 1:
            await ctx.send("Pone un numero mayor a 0 che")
            return
        
        from bot.config import ECONOMY_CONFIG
        ECONOMY_CONFIG['milestone_interval'] = intervalo
        await ctx.send(f"Ahora dan premio cada **{intervalo} mensajes**")

async def setup(bot):
    # esto es para cargar el modulo, no tocar
    await bot.add_cog(HelpCommand(bot))
