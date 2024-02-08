import discord
from typing import Optional

async def send_in_channel(interaction: discord.Interaction, message: Optional[str] = None, embed: Optional[discord.Embed] = None):
    channel = interaction.channel
    if isinstance(channel, discord.TextChannel):
        if embed:
            await channel.send(content=message, embed=embed)
        else:
            await channel.send(content=message)