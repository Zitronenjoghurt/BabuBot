import discord
from discord.ext import commands
from typing import Optional

async def retrieve_guild(bot: commands.Bot, guild_id: int) -> Optional[discord.Guild]:
    guild = bot.get_guild(guild_id)
    if isinstance(guild, discord.Guild):
        return guild
    try:
        guild: Optional[discord.Guild] = await bot.fetch_guild(guild_id)
        return guild
    except Exception:
        return None