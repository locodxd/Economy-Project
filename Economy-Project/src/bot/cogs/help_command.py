"""
Sistema de ayuda mejorado - Comando de ayuda personalizado con información detallada, esto es lo más facil de usar y entender.
"""

import discord
from discord.ext import commands
from typing import Optional

class HelpView(discord.ui.View):
    """Vista con botones para el comando help"""
    
    def __init__(self, ctx, bot):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.bot = bot
        self.message = None
    
    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.primary, custom_id="help_home")
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botón para mostrar ayuda general"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Solo quien usó el comando puede usar estos botones.", ephemeral=True)
            return
        
        embed = self.get_home_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="👑 Admin", style=discord.ButtonStyle.danger, custom_id="help_admin")
    async def admin_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botón para mostrar comandos admin"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Solo quien usó el comando puede usar estos botones.", ephemeral=True)
            return
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Necesitas permisos de administrador para ver estos comandos.", ephemeral=True)
            return
        
        embed = self.get_admin_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="⚔️ RPG", style=discord.ButtonStyle.success, custom_id="help_rpg")
    async def rpg_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botón para mostrar comandos RPG"""
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Solo quien usó el comando puede usar estos botones.", ephemeral=True)
            return
        
        embed = self.get_rpg_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def get_home_embed(self):
        """Genera el embed de ayuda general"""
        embed = discord.Embed(
            title="💰 Sistema de Economía",
            description="Usa `.help <comando>` para info detallada sobre un comando específico",
            color=discord.Color.gold()
        )
        
        basic_commands = [
            "`.daily` - Recompensa diaria",
            "`.weekly` - Recompensa semanal",
            "`.work` - Trabaja y gana",
            "`.balance` - Ver dinero",
            "`.deposit` - Al banco",
            "`.withdraw` - Del banco",
            "`.transfer` - Enviar dinero",
        ]
        embed.add_field(
            name="💵 Básicos",
            value="\n".join(basic_commands),
            inline=True
        )
        
        earn_commands = [
            "`.beg` - Mendiga",
            "`.search` - Busca dinero",
            "`.rob` - Roba usuario",
            "`.heist` - Atraco grande",
        ]
        embed.add_field(
            name="💸 Ganar Dinero",
            value="\n".join(earn_commands),
            inline=True
        )
        
        if self.bot.get_cog("Gambling"):
            casino_commands = [
                "`.coinflip` - Cara/cruz",
                "`.dice` - Dados",
                "`.slots` - Slots",
                "`.blackjack` - 21",
                "`.roulette` - Ruleta",
                "`.scratch` - Raspadita",
                "`.crash` - Crash",
            ]
            embed.add_field(
                name="🎰 Casino",
                value="\n".join(casino_commands),
                inline=True
            )
        
        shop_commands = [
            "`.tienda` - Ver items",
            "`.comprar` - Comprar",
            "`.inventario` - Ver bolso",
            "`.vender` - Vender",
        ]
        embed.add_field(
            name="🛒 Tienda",
            value="\n".join(shop_commands),
            inline=True
        )
        
        rpg_commands = [
            "`.rpg profile` - Stats",
            "`.rpg missions` - Misiones",
            "`.rpg mission` - Hacer",
            "`.rpg boss` - Pelear",
            "`.rpg heal` - Curar",
            "`.rpg abilities` - Ver",
            "`.rpg buy_ability` - Comprar",
        ]
        embed.add_field(
            name="⚔️ RPG",
            value="\n".join(rpg_commands),
            inline=True
        )
        
        extra_commands = [
            "`.wanted` - Tu nivel",
            "`.leaderboard` - Top users",
        ]
        embed.add_field(
            name="📊 Extra",
            value="\n".join(extra_commands),
            inline=True
        )
        
        embed.add_field(
            name="💡 Bonus",
            value="Escribe mensajes = ganas coins automáticamente!\nCada 100 mensajes = +1000 bonus",
            inline=False
        )
        
        embed.set_footer(text=f"Usa los botones para navegar | {len(self.bot.commands)} comandos")
        return embed
    
    def get_admin_embed(self):
        """Genera el embed de comandos admin"""
        embed = discord.Embed(
            title="👑 Comandos de Administrador",
            description="Comandos exclusivos para administradores del servidor.",
            color=discord.Color.red()
        )
        
        admin_commands = [
            "`/aeco_set` - Establecer dinero de usuario",
            "`/aeco_reset` - Resetear usuario",
            "`/aeco_add` - Añadir dinero",
            "`/aeco_remove` - Quitar dinero",
            "`/aeco_tienda` - Añadir item a la tienda",
            "`/aeco_info` - Ver info de usuario",
            "",
            "**Configuración del sistema:**",
            "`.setmilestone <cantidad>` - Cambiar recompensa por milestone",
            "`.setinterval <número>` - Cambiar intervalo de mensajes para milestone",
        ]
        
        embed.add_field(
            name="📋 Comandos Disponibles",
            value="\n".join(admin_commands),
            inline=False
        )
        
        embed.set_footer(text="Usa los comandos slash (/) para los comandos de economía")
        return embed
    
    def get_rpg_embed(self):
        """Genera el embed de comandos RPG"""
        embed = discord.Embed(
            title="⚔️ Sistema RPG",
            description="Haz misiones, pelea bosses y mejora tus habilidades",
            color=discord.Color.purple()
        )
        
        profile_commands = [
            "`.rpg profile` - Ver tus stats",
            "`.rpg missions` - Ver misiones",
        ]
        embed.add_field(
            name="📊 Info",
            value="\n".join(profile_commands),
            inline=True
        )
        
        mission_commands = [
            "`.rpg mission <id>` - Hacer misión",
            "`.rpg boss <id>` - Pelear boss",
            "`.rpg heal` - Curarte/Revivir",
        ]
        embed.add_field(
            name="⚡ Acción",
            value="\n".join(mission_commands),
            inline=True
        )
        
        ability_commands = [
            "`.rpg abilities` - Ver habilidades",
            "`.rpg buy_ability <id>` - Comprar",
        ]
        embed.add_field(
            name="✨ Habilidades",
            value="\n".join(ability_commands),
            inline=True
        )
        
        embed.add_field(
            name="💡 Habilidades disponibles",
            value="**luck** - 15% más dinero\n**grind** - Cooldowns 20% rápido\n**crit** - Crítico 20%\n**tank** - 20% menos daño",
            inline=False
        )
        
        return embed
    
    async def on_timeout(self):
        """Deshabilitar botones al expirar"""
        for item in self.children:
            item.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass

class HelpCommand(commands.Cog):
    """Sistema de ayuda personalizado"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help", aliases=["ayuda", "h"])
    async def help_command(self, ctx, comando: Optional[str] = None):
        """
        Muestra ayuda sobre los comandos
        
        Usa .help para ver todos los comandos
        Usa .help <comando> para información detallada
        """
        if comando:
            # Ayuda de comando específico
            cmd = self.bot.get_command(comando)
            if cmd:
                embed = discord.Embed(
                    title=f"📖 Ayuda: {cmd.name}",
                    description=cmd.help or "Sin descripción",
                    color=discord.Color.blue()
                )
                
                # Aliases
                if cmd.aliases:
                    embed.add_field(
                        name="📝 Aliases",
                        value=", ".join(f"`{alias}`" for alias in cmd.aliases),
                        inline=False
                    )
                
                # Uso
                usage = f".{cmd.name}"
                if cmd.signature:
                    usage += f" {cmd.signature}"
                embed.add_field(name="💡 Uso", value=f"`{usage}`", inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ No se encontró el comando `{comando}`")
        else:
            # Ayuda general con botones
            view = HelpView(ctx, self.bot)
            embed = view.get_home_embed()
            message = await ctx.send(embed=embed, view=view)
            view.message = message
    
    @commands.command(name="setmilestone")
    @commands.has_permissions(administrator=True)
    async def set_milestone_reward(self, ctx, cantidad: int):
        """Establecer la recompensa por milestone de mensajes"""
        if cantidad < 0:
            await ctx.send("❌ La cantidad debe ser positiva")
            return
        
        from bot.config import ECONOMY_CONFIG
        ECONOMY_CONFIG['milestone_reward'] = cantidad
        await ctx.send(f"✅ Recompensa por milestone establecida en **{cantidad:,} coins**")
    
    @commands.command(name="setinterval")
    @commands.has_permissions(administrator=True)
    async def set_milestone_interval(self, ctx, intervalo: int):
        """Establecer cada cuántos mensajes se da la recompensa milestone"""
        if intervalo < 1:
            await ctx.send("❌ El intervalo debe ser mayor a 0")
            return
        
        from bot.config import ECONOMY_CONFIG
        ECONOMY_CONFIG['milestone_interval'] = intervalo
        await ctx.send(f"✅ Intervalo de milestone establecido en **cada {intervalo} mensajes**")

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
