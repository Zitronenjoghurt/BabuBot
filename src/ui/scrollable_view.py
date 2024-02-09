import asyncio
import discord
from discord.ui import Button, View
from typing import Optional
from src.ui.scrollable_embed import ScrollableEmbed

class ScrollableView(View):
    def __init__(self, embed: ScrollableEmbed, user_id: int, timeout: float = 300, **kwargs):
        super().__init__(timeout=timeout, **kwargs)
        self.embed = embed
        self.user_id = user_id

        if not embed.is_scrollable():
            self.disable_buttons()
            self.stop()

        # Appending the message this view was attached to 
        # makes it possible to disable the buttons on timeout
        self.message: Optional[discord.InteractionMessage] = None

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previous_callback(self, interaction: discord.Interaction, button: Button):
        await self.embed.previous()
        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next_callback(self, interaction: discord.Interaction, button: Button):
        await self.embed.next()
        await interaction.response.edit_message(embed=self.embed)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self) -> None:
        self.embed.time_out()
        self.disable_buttons()
        if isinstance(self.message, discord.InteractionMessage):
            await self.message.edit(embed=self.embed, view=self)

    def disable_buttons(self) -> None:
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

    async def timeout_after(self, seconds: int):
        await asyncio.sleep(seconds)
        self.stop()
        await self.on_timeout()