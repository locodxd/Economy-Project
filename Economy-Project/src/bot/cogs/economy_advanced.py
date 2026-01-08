from discord.ext import commands
import random
from datetime import datetime
from src.core.economy_manager import EconomyManager

class EconomyAdvanced(commands.Cog):
    """Comandos avanzados de economía con características complejas"""

    def __init__(self, bot):
        self.bot = bot
        self.manager = EconomyManager()

    @commands.command(name="gamble", aliases=["apostar"])
    async def gamble(self, ctx, amount: int):
        """🎲 Apuesta una cantidad de dinero para ganar el doble o perderlo"""
        user_id = ctx.author.id
        user_data = await self.manager.get_user_data(user_id)

        if amount <= 0:
            await ctx.send("¡Debes apostar una cantidad positiva!")
            return

        if user_data.wallet < amount:
            await ctx.send("¡No tienes suficiente dinero para apostar!")
            return

        if random.choice([True, False]):
            await self.manager.add_money(user_id, amount, "wallet", "gamble_win")
            await ctx.send(f"¡Ganaste! Ahora tienes ${user_data.wallet + amount} en tu billetera.")
        else:
            await self.manager.remove_money(user_id, amount, "wallet", "gamble_loss")
            await ctx.send(f"¡Perdiste! Ahora tienes ${user_data.wallet - amount} en tu billetera.")

    @commands.command(name="daily_bonus", aliases=["bono_diario"])
    async def daily_bonus(self, ctx):
        """💰 Reclama tu bono diario"""
        user_id = ctx.author.id
        user_data = await self.manager.get_user_data(user_id)

        if user_data.last_daily_bonus and (datetime.now() - user_data.last_daily_bonus).days < 1:
            await ctx.send("¡Ya reclamaste tu bono diario hoy! Vuelve mañana.")
            return

        bonus = random.randint(500, 1500)
        await self.manager.add_money(user_id, bonus, "wallet", "daily_bonus")
        user_data.last_daily_bonus = datetime.now()
        await self.manager.save_user_data(user_data)

        await ctx.send(f"¡Recibiste un bono diario de ${bonus}! Ahora tienes ${user_data.wallet} en tu billetera.")

    @commands.command(name="transfer", aliases=["enviar"])
    async def transfer(self, ctx, member: commands.MemberConverter, amount: int):
        """💸 Transfiere dinero a otro usuario"""
        user_id = ctx.author.id
        target_id = member.id
        user_data = await self.manager.get_user_data(user_id)

        if amount <= 0:
            await ctx.send("¡Debes transferir una cantidad positiva!")
            return

        if user_data.wallet < amount:
            await ctx.send("¡No tienes suficiente dinero para transferir!")
            return

        await self.manager.remove_money(user_id, amount, "wallet", "transfer")
        await self.manager.add_money(target_id, amount, "wallet", "received_transfer")
        await ctx.send(f"¡Has transferido ${amount} a {member.display_name}!")

    @commands.command(name="leaderboard", aliases=["ranking"])
    async def leaderboard(self, ctx):
        """📊 Muestra el ranking de los usuarios con más dinero"""
        leaderboard_data = await self.manager.get_leaderboard()
        leaderboard_message = "🏆 **Ranking de Usuarios**\n"

        for rank, (user_id, balance) in enumerate(leaderboard_data, start=1):
            user = self.bot.get_user(user_id)
            leaderboard_message += f"{rank}. {user.display_name if user else 'Desconocido'} - ${balance}\n"

        await ctx.send(leaderboard_message)

async def setup(bot):
    await bot.add_cog(EconomyAdvanced(bot))