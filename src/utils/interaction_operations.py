import discord
from typing import Optional
from src.ui.scrollable_embed import ScrollableEmbed
from src.ui.scrollable_view import ScrollableView

async def send_in_channel(interaction: discord.Interaction, message: Optional[str] = None, embed: Optional[discord.Embed] = None):
    channel = interaction.channel
    if isinstance(channel, discord.TextChannel):
        if embed:
            await channel.send(content=message, embed=embed)
        else:
            await channel.send(content=message)

async def send_scrollable(interaction: discord.Interaction, embed: ScrollableEmbed, timeout_after: int = 120):
    if embed.scrollable.is_scrollable():
        scrollable_view = ScrollableView(embed=embed, user_id=interaction.user.id)
        await interaction.response.send_message(embed=embed, view=scrollable_view)
        scrollable_view.message = await interaction.original_response()
        await scrollable_view.timeout_after(timeout_after)
    else:
        await interaction.response.send_message(embed=embed)