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