import asyncio
import logging
from discord.ext import commands
from utils.tenor_core import get_tenor

logger = logging.getLogger('TenorCoreCog')


class TenorCoreCog(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.tenor = get_tenor()

	def cog_unload(self):
		try:
			loop = getattr(self.bot, 'loop', None)
			if loop and not loop.is_closed():
				loop.create_task(self.tenor.close())
			else:
				# fallback si no hay loop disponible
				asyncio.create_task(self.tenor.close())
		except Exception as e:
			logger.debug(f"Error cerrando Tenor session: {e}")


async def setup(bot):
	await bot.add_cog(TenorCoreCog(bot))

