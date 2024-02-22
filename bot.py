import discord
import json
from discord.ext import commands
from src.constants.config import Config
from src.entities.user import User
from src.logging.logger import LOGGER
from src.utils.command_operations import get_extensions

CONFIG = Config.get_instance()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix=CONFIG.PREFIX, intents=intents, enable_debug_events=True)

LOGGER.info("Bot initialized")

# Tomorrow is maths exam and I dont have the mental capacity to commit something BUT I dont wanna end my streak for 2024 so here it is, the commit of despair

@bot.event
async def on_ready():
    # Cache guilds
    for guild in bot.guilds:
        await guild.chunk()

    # Cache member data in database
    for user in await User.findall():
        print(user.userid)
        await user.cache_member_data(bot)
        await user.save()
    LOGGER.info("Cached available member data of all users in database")

    # Load extensions
    extensions = get_extensions()
    for extension in extensions:
        await bot.load_extension(extension)

    # Set activity
    await bot.change_presence(activity=discord.Game(name="try: /tasks"))

    LOGGER.info("Bot ready")

# Connection events
@bot.event
async def on_connect():
    LOGGER.info("Bot connected")

@bot.event
async def on_disconnect():
    LOGGER.warn("Bot disconnected")

@bot.event
async def on_resumed():
    LOGGER.info("Bot reconnected")

@bot.event
async def on_socket_raw_receive(msg):
    try:
        data = json.loads(msg)
    except Exception:
        return
    if not isinstance(data, dict):
        return
    opcode = data.get('op', None)
    match opcode:
        case 7:
            LOGGER.info('Received opcode 7: Reconnect requested by Discord')
        case 9:
            LOGGER.error('Received opcode 9: Session has been invalidated')
        
bot.run(CONFIG.BOT_TOKEN)