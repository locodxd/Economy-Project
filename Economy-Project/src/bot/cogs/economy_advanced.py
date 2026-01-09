from discord.ext import commands
import random
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.economy_manager import EconomyManager

class EconomyAdvanced(commands.Cog):
    """Comandos avanzados de economía con características complejas"""

    def __init__(self, bot):
        self.bot = bot
        self.manager = EconomyManager()

    @commands.command(name="gamble", aliases=["apostar"])
    async def gamble(self, ctx, amount: int):
        """ Apuesta una cantidad de dinero para ganar el doble o perderlo"""
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
        """ Reclama tu bono diario"""
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

async def setup(bot):
    await bot.add_cog(EconomyAdvanced(bot))