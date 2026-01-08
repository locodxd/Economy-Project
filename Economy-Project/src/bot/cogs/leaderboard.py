from discord.ext import commands
import discord

class Leaderboard(commands.Cog):
    """Comandos para manejar el leaderboard de usuarios"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        """📊 Muestra el leaderboard de usuarios basado en riqueza"""
        # Aquí se debería obtener la información del leaderboard desde la base de datos
        # Por simplicidad, se usará una lista de ejemplo
        leaderboard_data = [
            {"username": "Usuario1", "wealth": 10000},
            {"username": "Usuario2", "wealth": 8000},
            {"username": "Usuario3", "wealth": 6000},
            {"username": "Usuario4", "wealth": 4000},
            {"username": "Usuario5", "wealth": 2000},
        ]

        embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())
        for index, user in enumerate(leaderboard_data, start=1):
            embed.add_field(name=f"{index}. {user['username']}", value=f"💰 ${user['wealth']:,}", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))