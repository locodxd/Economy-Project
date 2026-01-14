"""
cog deshabilitado, mantener por legado
"""

from discord.ext import commands

class EconomyAdvanced(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Este cog está deshabilitado porque usa EconomyManager obsoleto

async def setup(bot):
    pass