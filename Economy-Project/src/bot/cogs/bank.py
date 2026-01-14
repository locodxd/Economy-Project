from discord.ext import commands
import random

class MessageContainer:
    """Contenedor simple para almacenar mensajes"""
    def __init__(self):
        self.msgs = []

class Bank(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        # Inicializar contenedores de mensajes
        self.poor = MessageContainer()
        self.rich = MessageContainer()
        self.normal = MessageContainer()

        self.poor.msgs = [
            "No tenés un mango, andá a laburar.",
            "Tu cuenta bancaria está más vacía que mi heladera.",
            "Parece que sos más pobre que una rata.",
            "No tenés ni para un café, qué triste.",
            "Tu saldo es tan bajo que da vergüenza ajena.",
        ]

        self.rich.msgs = [
            "Sos más rico que un jeque árabe.",
            "Tu cuenta bancaria está llena de billetes, qué envidia.",
            "Parece que sos más rico que Bill Gates.",
            "Tenés tanto dinero que podrías comprar un yate.",
            "Tu saldo es tan alto que da miedo.",
        ]

        self.normal.msgs = [
            "Tenés una cantidad decente de dinero.",
            "Tu cuenta bancaria está equilibrada.",
            "Parece que sos una persona financieramente responsable.",
            "Tenés suficiente dinero para vivir cómodamente.",
            "Tu saldo es estable, buen trabajo.",
        ]

    @commands.command(name="bankinfo", aliases=["bi", "bankstats"])
    async def bank_info(self, ctx):
        balance = 1000

        if balance < 1000:
            msg = random.choice(self.poor.msgs)
        elif balance > 100000:
            msg = random.choice(self.rich.msgs)
        else:
            msg = random.choice(self.normal.msgs)

        await ctx.send(
            f"Tu saldo es de {balance} monedas. {msg}"
              
        )
async def setup(bot):
    await bot.add_cog(Bank(bot))