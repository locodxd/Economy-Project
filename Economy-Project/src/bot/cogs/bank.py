from discord.ext import commands

class Bank(commands.Cog):
    """Comandos bancarios para gestionar las finanzas de los usuarios."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bankinfo", aliases=["bi", "bankstats"])
    async def bank_info(self, ctx):
        """checkea tu balance bancario"""
        balance = 1000  # Placeholder value
        await ctx.send(f"Tu balance del banco es ${balance}.")

async def setup(bot):
    await bot.add_cog(Bank(bot))