import discord
from discord.ext import commands
from src.constants.config import Config
from src.entities.user import User
from src.utils.command_operations import get_extensions

CONFIG = Config.get_instance()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="%", intents=intents)

@bot.event
async def on_ready():
    # Load extensions
    extensions = get_extensions()
    for extension in extensions:
        await bot.load_extension(extension)

    # Set activity
    await bot.change_presence(activity=discord.Game(name="The Bobbing Bobs"))

    print(f'Logged in as {bot.user.name}')

bot.run(CONFIG.BOT_TOKEN)