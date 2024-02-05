import discord
from discord.ext import commands
from src.constants.config import Config
from src.logging.logger import LOGGER
from src.utils.command_operations import get_extensions

CONFIG = Config.get_instance()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix=CONFIG.PREFIX, intents=intents)

LOGGER.info("Bot initialized")

@bot.event
async def on_connect():
    LOGGER.info("Bot connected")

@bot.event
async def on_ready():
    # Cache guilds
    for guild in bot.guilds:
        await guild.chunk()

    # Load extensions
    extensions = get_extensions()
    for extension in extensions:
        await bot.load_extension(extension)

    # Set activity
    await bot.change_presence(activity=discord.Game(name="send ideas: /feedback"))

    LOGGER.info("Bot ready")

@bot.event
async def on_disconnect():
    LOGGER.info("Bot disconnected")

bot.run(CONFIG.BOT_TOKEN)