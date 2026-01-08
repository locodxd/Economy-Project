from discord.ext import commands
import random
from datetime import datetime

class EconomyBasic(commands.Cog):
    """Comandos básicos de economía"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="daily", aliases=["d"])
    async def daily(self, ctx):
        """Reclama tu recompensa diaria"""
        user_id = ctx.author.id
        base_reward = 1000
        streak_bonus = 0  # Placeholder for streak bonus logic
        final_reward = base_reward + streak_bonus

        # Simulate adding money to user's balance
        await ctx.send(f"{ctx.author.mention}, has reclamado tu daily de ${final_reward}!")

    @commands.command(name="work", aliases=["trabajar"])
    async def work(self, ctx):
        """Trabaja para ganar dinero"""
        jobs = ["repartidor", "programador", "diseñador", "mecánico"]
        job = random.choice(jobs)
        earnings = random.randint(100, 500)
        
        await ctx.send(f"{ctx.author.mention}, trabajaste como {job} y ganaste ${earnings}!")

    @commands.command(name="transfer", aliases=["enviar"])
    async def transfer(self, ctx, member: commands.MemberConverter, amount: int):
        """Transfiere dinero a otro usuario"""
        if amount <= 0:
            await ctx.send("El monto debe ser mayor que 0.")
            return
        
        # Simulate transfer logic
        await ctx.send(f"{ctx.author.mention}, has transferido ${amount} a {member.mention}!")

    @commands.command(name="beg", aliases=["mendigar"])
    async def beg(self, ctx):
        """Pide dinero a otros usuarios"""
        amount = random.randint(5, 100)
        await ctx.send(f"{ctx.author.mention}, has mendigado y recibido ${amount}!")

    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx):
        """Muestra tu balance actual"""
        # Simulate fetching user balance
        balance = random.randint(1000, 5000)
        await ctx.send(f"{ctx.author.mention}, tu balance actual es ${balance}.")

async def setup(bot):
    await bot.add_cog(EconomyBasic(bot))