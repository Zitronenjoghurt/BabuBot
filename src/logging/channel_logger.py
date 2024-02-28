import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional
from src.constants.config import Config
from src.logging.logger import LOGGER
from src.utils.string_operations import limit_length

CONFIG = Config.get_instance()

class ChannelLogger():
    _instance = None

    def __init__(self, bot: Optional[commands.Bot]) -> None:
        if ChannelLogger._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of ChannelLogger.")
        if not isinstance(bot, commands.Bot):
            raise RuntimeError("Tried to initialize ChannelLogger without a bot instance.")
        self.bot = bot
        self.channels: dict[str, discord.TextChannel] = {}
        self.initialized = False

    @staticmethod
    async def _initialize(bot: Optional[commands.Bot] = None) -> 'ChannelLogger':
        ChannelLogger._instance = ChannelLogger(bot=bot)
        CL = ChannelLogger.get_instance()

        try:
            default_channel = await CL.bot.fetch_channel(CONFIG.LOG_CHANNEL_ID)
        except Exception as e:
            raise RuntimeError(f"An error occured while initializing the ChannelLogger: Unable to fetch log channel {CONFIG.LOG_CHANNEL_ID}.")
        
        if not isinstance(default_channel, discord.TextChannel):
            raise RuntimeError(f"An error occured while initializing the ChannelLogger: Specified log channel is not a TextChannel.")

        CL.channels['default'] = default_channel
        CL.initialized = True
        LOGGER.info("ChannelLogger initialized.")

        return CL

    @staticmethod
    def get_instance() -> 'ChannelLogger':
        if ChannelLogger._instance is None:
            raise RuntimeError(f"An error occured while getting instance of ChannelLogger: ChannelLogger was not initialized yet. Use _initialize and pass a bot instance.")
        return ChannelLogger._instance
    
    def get_log_channel(self, log_channel: Optional[str] = None) -> discord.TextChannel:
        default_channel = self.channels.get("default")
        if not isinstance(default_channel, discord.TextChannel):
            raise RuntimeError(f"An error occured while retrieving default logging channel: channel is not a TextChannel.")
        
        if not isinstance(log_channel, str):
            return default_channel
        
        channel = self.channels.get(log_channel)
        if not isinstance(channel, discord.TextChannel):
            return default_channel
        return channel

    async def info(self, message: str, log_channel: Optional[str] = None, title: Optional[str] = None, author_name: Optional[str] = None, icon_url: Optional[str] = None, fields: Optional[list[tuple[str, str]]] = None) -> None:
        await self.log(color="#3474EB", log_channel=log_channel, message=message, title=title, author_name=author_name, icon_url=icon_url, fields=fields)

    async def dm(self, message: discord.Message, log_channel: Optional[str] = None) -> None:
        content = message.content
        if not isinstance(content, str):
            content = ""
        author = message.author
        await self.log(color="#68E397", log_channel=log_channel, message=content, title="DM RECEIVED", author_name=author.name, icon_url=author.display_avatar.url)

    async def log(self, message: str, color: str, log_channel: Optional[str] = None, title: Optional[str] = None, author_name: Optional[str] = None, icon_url: Optional[str] = None, fields: Optional[list[tuple[str, str]]] = None) -> None:
        if not isinstance(message, str):
            raise ValueError("Log message must be a string.")
        if not isinstance(color, str):
            raise ValueError("Log color must be a string.")
        if title and not isinstance(title, str):
            raise ValueError("Log title must be a string.")
        if author_name and not isinstance(author_name, str):
            raise ValueError("Log author_name must be a string.")
        if icon_url and not isinstance(icon_url, str):
            raise ValueError("Log icon_url must be a string.")
        
        if fields:
            for value, name in fields:
                if not isinstance(value, str) or not isinstance(name, str):
                    raise ValueError("All log fielt titles and names have to be strings.")
        
        if title:
            title = limit_length(title, 256)
        message = limit_length(message, 4000)
        
        channel = self.get_log_channel(log_channel=log_channel)
        embed = build_embed(title, message, author_name, icon_url, fields)
        embed.color = discord.Color.from_str(color)
        await channel.send(embed=embed)

def build_embed(title: Optional[str] = None, message: Optional[str] = None, author_name: Optional[str] = None, icon_url: Optional[str] = None, fields: Optional[list[tuple[str, str]]] = None) -> discord.Embed:
    embed = discord.Embed(title=title, description=message, timestamp=datetime.now())
    if author_name:
        embed.set_author(name=author_name, icon_url=icon_url)
    if fields:
        for name, value in fields:
            embed.add_field(name=name, value=value)
    return embed