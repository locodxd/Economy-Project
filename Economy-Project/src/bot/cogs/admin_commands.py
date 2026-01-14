"""
Comandos de administración de economía
"""

import discord
from discord import app_commands
from discord.ext import commands
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db
from bot.utils.auth import is_config_admin_app

class AdminCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    def is_admin(interaction: discord.Interaction) -> bool:
        """Deprecated. Use EZ-config admin check instead."""
        return interaction.user.guild_permissions.administrator
    
    @app_commands.command(name="aeco_set", description="Establece el dinero de un usuario")
    @is_config_admin_app()
    async def aeco_set(
        self, 
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int,
        tipo: str = "wallet"
    ):
        """
        Establece el dinero de un usuario
        
        Args:
            usuario: El usuario a modificar
            cantidad: Cantidad de dinero
            tipo: 'wallet' o 'bank' (por defecto: wallet)
        """
        if tipo not in ["wallet", "bank"]:
            await interaction.response.send_message(
                "❌ El tipo debe ser 'wallet' o 'bank'",
                ephemeral=True
            )
            return
        
        if cantidad < 0:
            await interaction.response.send_message(
                "❌ La cantidad no puede ser negativa",
                ephemeral=True
            )
            return
        
        user_data = db.get_user(str(usuario.id))
        user_data[tipo] = cantidad
        db.update_user(str(usuario.id), user_data)
        
        embed = discord.Embed(
            title="✅ Dinero Establecido",
            description=f"Se estableció **${cantidad:,}** en el **{tipo}** de {usuario.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Admin: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aeco_reset", description="Resetea completamente la economía de un usuario")
    @is_config_admin_app()
    async def aeco_reset(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        """
        Resetea completamente todos los datos económicos de un usuario
        
        Args:
            usuario: El usuario a resetear
        """
        db.reset_user(str(usuario.id))
        
        embed = discord.Embed(
            title="🔄 Usuario Reseteado",
            description=f"Se han reseteado todos los datos económicos de {usuario.mention}",
            color=discord.Color.orange()
        )
        embed.add_field(name=" Wallet", value="$0", inline=True)
        embed.add_field(name=" Bank", value="$0", inline=True)
        embed.add_field(name=" Inventario", value="Vacío", inline=True)
        embed.set_footer(text=f"Admin: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aeco_add", description="Añade dinero a un usuario")
    @is_config_admin_app()
    async def aeco_add(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int,
        tipo: str = "wallet"
    ):
        """
        Añade dinero a un usuario
        
        Args:
            usuario: El usuario
            cantidad: Cantidad a añadir
            tipo: 'wallet' o 'bank'
        """
        if tipo not in ["wallet", "bank"]:
            await interaction.response.send_message(
                " El tipo debe ser 'wallet' o 'bank'",
                ephemeral=True
            )
            return
        
        if cantidad <= 0:
            await interaction.response.send_message(
                " Bro la cantidad debe ser positiva",
                ephemeral=True
            )
            return
        
        db.add_money(str(usuario.id), cantidad, tipo)
        
        embed = discord.Embed(
            title="➕ Dinero Añadido",
            description=f"Se añadieron **${cantidad:,}** al **{tipo}** de {usuario.mention}",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Admin: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aeco_remove", description="Quita dinero a un usuario")
    @is_config_admin_app()
    async def aeco_remove(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int,
        tipo: str = "wallet"
    ):
        """
        Quita dinero al jugador seleccionado
        
        Args:
            usuario: El usuario
            cantidad: Cantidad a quitar
            tipo: 'wallet' o 'bank'
        """
        if tipo not in ["wallet", "bank"]:
            await interaction.response.send_message(
                " El tipo debe ser 'wallet' o 'bank'",
                ephemeral=True
            )
            return
        
        if cantidad <= 0:
            await interaction.response.send_message(
                " Bro la cantidad debe ser positiva",
                ephemeral=True
            )
            return
        
        success = db.remove_money(str(usuario.id), cantidad, tipo)
        
        if success:
            embed = discord.Embed(
                title="➖ Dinero Quitado",
                description=f"Se quitaron **${cantidad:,}** del **{tipo}** de {usuario.mention}",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Admin: {interaction.user.name}")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f" {usuario.mention} no tiene suficiente dinero en su {tipo}",
                ephemeral=True
            )
    
    @app_commands.command(name="aeco_tienda", description="Añade un item a la tienda del servidor")
    @is_config_admin_app()
    @app_commands.describe(cantidad='cantidad disponible (1 o más, escribe \'infinito\' para ilimitado)')
    async def aeco_tienda(
        self,
        interaction: discord.Interaction,
        nombre: str,
        precio: int,
        cantidad: str,
        descripcion: str = "Sin descripción"
    ):
        """
        Añade un item a la tienda del servidor
        
        Args:
            nombre: Nombre del item (ej: Discord Nitro)
            precio: Precio en monedas
            descripcion: Descripción del item
        """
        import json
        from pathlib import Path
        
        if cantidad.lower() == "infinito":
            cantidad_final = -1 
        else:
            try:
                cantidad_final = int(cantidad)
                if cantidad_final < 1:
                    await interaction.response.send_message('la cantidad debe ser 1 o más, o "infinito"', ephemeral=True)
                    return
            except ValueError:
                await interaction.response.send_message('la cantidad debe ser un número entero o "infinito"', ephemeral=True)
                return
            
        shop_path = Path("database/shop_items.json")
        shop_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar tienda actual
        shop_data = {}
        if shop_path.exists():
            with open(shop_path, 'r', encoding='utf-8') as f:
                shop_data = json.load(f)
        
        # Obtener items del servidor
        guild_id = str(interaction.guild.id)
        if guild_id not in shop_data:
            shop_data[guild_id] = []
        
        # Añadir item
        item = {
            "nombre": nombre,
            "precio": precio,
            "cantidad": cantidad_final,
            "descripcion": descripcion,
            "añadido_por": interaction.user.id,
            "fecha": discord.utils.utcnow().isoformat()
        }
        shop_data[guild_id].append(item)
        
        # Guardar
        with open(shop_path, 'w', encoding='utf-8') as f:
            json.dump(shop_data, f, indent=2, ensure_ascii=False)
        
        embed = discord.Embed(
            title="🛒 Item Añadido a la Tienda",
            description=f"**{nombre}** ha sido añadido a la tienda del servidor",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Precio", value=f"${precio:,}", inline=True)
        embed.add_field(name="📝 Descripción", value=descripcion, inline=False)
        embed.set_footer(text=f"Admin: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="aeco_info", description="Muestra información detallada de un usuario")
    @app_commands.check(is_admin)
    async def aeco_info(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        """
        Muestra información económica completa de un usuario
        
        Args:
            usuario: El usuario a consultar
        """
        user_data = db.get_user(str(usuario.id))
        
        embed = discord.Embed(
            title=f"📊 Información de {usuario.display_name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.add_field(name="💰 Wallet", value=f"${user_data.get('wallet', 0):,}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"${user_data.get('bank', 0):,}", inline=True)
        embed.add_field(name="💎 Total", value=f"${user_data.get('wallet', 0) + user_data.get('bank', 0):,}", inline=True)
        embed.add_field(name="📈 Ganado Total", value=f"${user_data.get('total_earned', 0):,}", inline=True)
        embed.add_field(name="📉 Gastado Total", value=f"${user_data.get('total_spent', 0):,}", inline=True)
        embed.add_field(name="⭐ Nivel", value=str(user_data.get('level', 1)), inline=True)
        embed.add_field(name="🔥 Racha Daily", value=f"{user_data.get('daily_streak', 0)} días", inline=True)
        embed.set_footer(text=f"ID: {usuario.id}")
        
        await interaction.response.send_message(embed=embed)
    
    @aeco_set.error
    @aeco_reset.error
    @aeco_add.error
    @aeco_remove.error
    @aeco_tienda.error
    @aeco_info.error
    async def admin_command_error(self, interaction: discord.Interaction, error):
        """Manejo de errores para comandos admin"""
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                " Solo los administradores pueden usar este comando, porque intentas esto.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f" Ocurrió un error: {str(error)}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
