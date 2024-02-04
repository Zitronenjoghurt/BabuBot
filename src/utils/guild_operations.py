import asyncio
import discord
from typing import Optional

async def retrieve_member(guild: discord.Guild, member_id: int) -> Optional[discord.Member]:
    member = guild.get_member(member_id)
    if isinstance(member, discord.Member):
        return member
    try:
        member: Optional[discord.Member] = await guild.fetch_member(member_id)
        return member
    except Exception:
        return None
    
async def retrieve_members(guild: discord.Guild, member_ids: list[int]) -> dict[int, discord.Member]:
    members = await asyncio.gather(*(retrieve_member(guild, member_id) for member_id in member_ids))
    return {member.id: member for member in members if isinstance(member, discord.Member)}