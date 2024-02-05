import asyncio
import discord
from typing import Optional
from src.logging.logger import LOGGER

async def retrieve_member(guild: discord.Guild, member_id: int) -> Optional[discord.Member]:
    member = guild.get_member(member_id)
    if isinstance(member, discord.Member):
        LOGGER.debug(f"retrieve_member {member_id} cache hit")
        return member
    try:
        LOGGER.debug(f"retrieve_member {member_id} cache miss")
        member: Optional[discord.Member] = await guild.fetch_member(member_id)
        return member
    except Exception as e:
        LOGGER.error(f"An error occured trying to retrieve member {member_id}: {e}")
        return None
    
async def retrieve_member_strict(guild: discord.Guild, member_id: int) -> discord.Member:
    member = await retrieve_member(guild=guild, member_id=member_id)
    if not isinstance(member, discord.Member):
        LOGGER.critical("Failed to retrieve member.")
        raise RuntimeError("Unable to retrieve member.")
    return member
    
async def retrieve_members(guild: discord.Guild, member_ids: list[int]) -> dict[int, discord.Member]:
    members = await asyncio.gather(*(retrieve_member(guild, member_id) for member_id in member_ids))
    return {member.id: member for member in members if isinstance(member, discord.Member)}