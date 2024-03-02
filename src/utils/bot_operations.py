import asyncio
import discord
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.entities.user import User
from src.logging.logger import LOGGER
from src.utils.message_operations import get_ai_context_from_message
from src.utils.guild_operations import retrieve_member

CONFIG = Config.get_instance()

async def retrieve_guild(bot: commands.Bot, guild_id: int) -> Optional[discord.Guild]:
    guild = bot.get_guild(guild_id)
    if isinstance(guild, discord.Guild):
        #LOGGER.debug(f"retrieve_guild {guild_id} cache hit")
        return guild
    try:
        #LOGGER.debug(f"retrieve_guild {guild_id} cache miss")
        guild: Optional[discord.Guild] = await bot.fetch_guild(guild_id)
        return guild
    except Exception as e:
        LOGGER.error(f"An error occured trying to retrieve guild {guild_id}: {e}")
        return None
    
async def retrieve_guild_strict(bot: commands.Bot, guild_id: int) -> discord.Guild:
    guild = await retrieve_guild(bot=bot, guild_id=guild_id)
    if not isinstance(guild, discord.Guild):
        LOGGER.critical("Failed to retrieve guild.")
        raise RuntimeError("Unable to retrieve guild.")
    
    return guild

async def cache_member_data(bot: commands.Bot, user: User, member: Optional[discord.Member] = None) -> None:
    if not member:
        guild = await retrieve_guild_strict(bot=bot, guild_id=CONFIG.GUILD_ID)
        member = await retrieve_member(guild=guild, member_id=int(user.userid))
        if not member:
            LOGGER.debug(f"Tried to cache member data of id {user.userid} in database but member was not found")
            return

    user.name = member.name
    user.display_name = member.display_name
    LOGGER.debug(f"Cached member data of id {user.userid} in database")

async def send_in_channel(bot: commands.Bot, channel_id: int, content: Optional[str] = None, embed: Optional[discord.Embed] = None) -> bool:
    if not content and not embed:
        LOGGER.error(f"bot_operations failed to send message in channel {channel_id}: No content or embed provided.")
        return False
    if content and not isinstance(content, str):
        LOGGER.error(f"bot_operations failed to send message in channel {channel_id}: Content has to be of type string.")
        return False
    if embed and not isinstance(embed, discord.Embed):
        LOGGER.error(f"bot_operations failed to send message in channel {channel_id}: Embed has to be a valid discord Embed.")
        return False
    
    channel = await bot.fetch_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        LOGGER.error(f"bot_operations failed to send message in channel {channel_id}: Channel is not a TextChannel or does not exist.")
        return False
    
    try:
        await channel.send(content=content, embed=embed) # type: ignore
        return True
    except Exception as e:
        LOGGER.error(f"bot_operations failed to send message in channel {channel_id}: {e}")
        return False
    
async def get_message_context(bot: commands.Bot, message: discord.Message, context_length: int = 20) -> list[str]:
    channel = message.channel
    if not isinstance(channel, discord.TextChannel):
        return []
    
    context_messages = []
    async for msg in channel.history(limit=context_length*2, before=message):
        context = await get_ai_context_from_message(message=msg)
        if len(context) == 0:
            continue
        context_messages.append(context)

    if len(context_messages) > context_length - 1:
        context_messages = context_messages[:context_length]

    context_messages.reverse()

    author_context = await get_ai_context_from_message(message=message)
    if len(author_context) > 0:
        context_messages.append(author_context)

    return context_messages

async def notify_user(bot: commands.Bot, user_id: int, delay_seconds: int = 0, try_dm: bool = False, channel_id: Optional[int] = None, message: Optional[str] = None, embed: Optional[discord.Embed] = None):
    if delay_seconds < 0:
            delay_seconds = 0
    await asyncio.sleep(delay=delay_seconds)

    dm_success = None
    if try_dm:
        dm_success = await notify_user_private(bot=bot, user_id=user_id, message=message, embed=embed)
        if dm_success:
            return
    
    if not channel_id:
        raise RuntimeError(f"An error occured while notifying user {user_id}: no channel id specified. try_dm: {try_dm}, dm_success: {dm_success}")
    
    channel_success = await notify_user_channel(bot=bot, user_id=user_id, channel_id=channel_id, message=message, embed=embed)
    if not channel_success:
        raise RuntimeError(f"Unable to notify user {user_id} in channel {channel_id}. try_dm: {try_dm}, dm_success: {dm_success}")

async def notify_user_private(bot: commands.Bot, user_id: int, message: Optional[str] = None, embed: Optional[discord.Embed] = None) -> bool:
    try:
        user = await bot.fetch_user(user_id)
        if not isinstance(user, discord.User):
            LOGGER.error(f"Tried to notify user {user_id} via DM: unable to retrieve user.")
            return False
        dm_channel = await user.create_dm()

        content_available = isinstance(message, str)
        embed_available = isinstance(embed, discord.Embed)
        if content_available and embed_available:
            await dm_channel.send(content=message, embed=embed)
        elif content_available:
            await dm_channel.send(content=message)
        elif embed_available:
            await dm_channel.send(embed=embed)
        else:
            LOGGER.error(f"Tried to notify user {user_id} via DM: no message or embed was provided.")
            return False
        
        return True
    except Exception as e:
        LOGGER.error(f"An error occured while trying to notify user {user_id} via DM: {e}")
        return False
    
async def notify_user_channel(bot: commands.Bot, user_id: int, channel_id: int, message: Optional[str] = None, embed: Optional[discord.Embed] = None) -> bool:
    try:
        user = await bot.fetch_user(user_id)
        channel = await bot.fetch_channel(channel_id)

        if not isinstance(user, discord.User):
            LOGGER.error(f"Tried to notify user {user_id} in channel {channel_id}: unable to retrieve user.")
            return False
        if not isinstance(channel, discord.TextChannel):
            LOGGER.error(f"Tried to notify user {user_id} in channel {channel_id}: unable to retrieve channel.")
            return False
        
        content_available = isinstance(message, str)
        embed_available = isinstance(embed, discord.Embed)
        if not content_available and not embed_available:
            LOGGER.error(f"Tried to notify user {user_id} in channel {channel_id}: unable to retrieve channel.")
            return False

        if content_available:
            message = f"<@{user_id}>,\n{message}"
        else:
            message = f"<@{user_id}>"
        
        if embed_available:
            await channel.send(content=message, embed=embed)
        else:
            await channel.send(content=message)
        return True
    except Exception as e:
        LOGGER.error(f"An error occured while trying to notify user {user_id} in channel {channel_id}: {e}")
        return False