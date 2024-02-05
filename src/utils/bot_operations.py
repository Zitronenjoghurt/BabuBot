import discord
from discord.ext import commands
from typing import Optional
from src.logging.logger import LOGGER

async def retrieve_guild(bot: commands.Bot, guild_id: int) -> Optional[discord.Guild]:
    guild = bot.get_guild(guild_id)
    if isinstance(guild, discord.Guild):
        LOGGER.debug(f"retrieve_guild {guild_id} cache hit")
        return guild
    try:
        LOGGER.debug(f"retrieve_guild {guild_id} cache miss")
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