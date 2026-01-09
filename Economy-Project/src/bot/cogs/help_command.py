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
    
    def get_home_embed(self):
        """Genera el embed de ayuda general"""
        embed = discord.Embed(
            title="💰 Sistema de Economía - Ayuda",
            description="Usa `.help <comando>` para información detallada sobre un comando.",
            color=discord.Color.gold()
        )
        
        # Comandos básicos
        basic_commands = [
            "`.daily` - Recompensa diaria (24h)",
            "`.work` - Trabaja para ganar dinero (1h)",
            "`.balance` - Ver tu dinero",
            "`.beg` - Mendiga dinero (5min)",
            "`.deposit` - Depositar en el banco",
            "`.withdraw` - Retirar del banco",
            "`.transfer` - Transferir dinero a otro usuario",
        ]
        embed.add_field(
            name="💵 Comandos Básicos",
            value="\n".join(basic_commands),
            inline=False
        )
        
        # Comandos de casino
        if self.bot.get_cog("Gambling"):
            casino_commands = [
                "`.coinflip` - Cara o cruz",
                "`.dice` - Lanza los dados",
                "`.slots` - Máquina tragamonedas",
            ]
            embed.add_field(
                name="🎰 Casino",
                value="\n".join(casino_commands),
                inline=False
            )
        
        # Comandos de tienda
        if self.bot.get_cog("Shop"):
            shop_commands = [
                "`.shop` - Ver la tienda",
                "`.buy` - Comprar un item",
                "`.inventory` - Ver tu inventario",
            ]
            embed.add_field(
                name="🛒 Tienda",
                value="\n".join(shop_commands),
                inline=False
            )
        
        embed.add_field(
            name="💡 Tip",
            value="Escribe mensajes en el servidor para ganar monedas automáticamente!\n¡Cada 100 mensajes recibes 1000 coins de bonus!",
            inline=False
        )
        
        embed.set_footer(text=f"Prefijo: . | Total de comandos: {len(self.bot.commands)}")
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
                
                # Cooldown
                if cmd._buckets._cooldown:
                    cooldown = cmd._buckets._cooldown
                    embed.add_field(
                        name="⏱️ Cooldown",
                        value=f"{cooldown.rate} uso(s) cada {cooldown.per}s",
                        inline=False
                    )
                
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
