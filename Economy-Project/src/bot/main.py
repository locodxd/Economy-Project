import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '!'

# Initialize bot
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.default())

# Load cogs
async def load_cogs():
    for filename in os.listdir('./src/bot/cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    logging.info(f'Bot connected as {bot.user}')
    await load_cogs()
    logging.info(f'Loaded {len(bot.cogs)} cogs.')

if __name__ == '__main__':
    bot.run(TOKEN)