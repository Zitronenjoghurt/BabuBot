import discord
from discord.ui import Button, View
from typing import Optional

class ConfirmView(View):
    def __init__(self, user_id: int, timeout: float = 180, **kwargs):
        super().__init__(timeout=timeout, **kwargs)
        self.user_id = user_id
        self.confirmed = False

        # Appending the message this view was attached to 
        # makes it possible to disable the buttons on timeout
        self.message: Optional[discord.InteractionMessage] = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_callback(self, interaction: discord.Interaction, button: Button):
        self.confirmed = True
        self.disable_buttons()
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_callback(self, interaction: discord.Interaction, button: Button):
        self.confirmed = False
        self.disable_buttons()
        await interaction.response.edit_message(view=self)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self) -> None:
        self.confirmed = False
        self.disable_buttons()
        if isinstance(self.message, discord.InteractionMessage):
            await self.message.edit(view=self)

    def disable_buttons(self) -> None:
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True