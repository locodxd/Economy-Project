from discord.ext import commands

class Bank(commands.Cog):
    """Bank commands for managing user finances."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bankinfo", aliases=["bi", "bankstats"])
    async def bank_info(self, ctx):
        """Check your bank account balance."""
        # la logica para obtener el balance del usuario iria aqui
        # ejemplo: balance = await self.manager.get_balance(ctx.author.id)
        balance = 1000  # Placeholder value
        await ctx.send(f"Your current bank balance is ${balance}.")

async def setup(bot):
    await bot.add_cog(Bank(bot))