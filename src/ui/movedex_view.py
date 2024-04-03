import asyncio
import discord
from discord.ui import Button, View
from typing import Optional
from src.constants.emoji_index import EmojiIndex
from src.entities.pokemon.move import PokemonMove, MoveEmbed

EMOJI_INDEX = EmojiIndex.get_instance()

class MovedexView(View):
    def __init__(self, move: PokemonMove, user_id: int, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.move = move
        self.user_id = user_id
        self.embeds: dict[str, MoveEmbed] = {}
        self.current_embed = "general"

        self.message: Optional[discord.InteractionMessage] = None

    async def _generate_embeds(self) -> None:
        self.embeds["general"] = self.move.generate_general_embed()
        self.embeds["effect"] = self.move.generate_effect_embed()

        disabled_embeds = []
        for id, embed in self.embeds.items():
            if embed.disabled:
                disabled_embeds.append(id)

        for child in self.children:
            if isinstance(child, Button) and child.custom_id in disabled_embeds:
                child.disabled = True

    @discord.ui.button(emoji="ℹ️", style=discord.ButtonStyle.primary, custom_id="general")
    async def general_button(self, interaction: discord.Interaction, button: Button):
        self.current_embed = "general"
        await interaction.response.edit_message(embed=self.embeds["general"])

    @discord.ui.button(emoji="📖", style=discord.ButtonStyle.secondary, custom_id="effect")
    async def effect_button(self, interaction: discord.Interaction, button: Button):
        self.current_embed = "effect"
        await interaction.response.edit_message(embed=self.embeds["effect"])

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self) -> None:
        self.disable_buttons()
        self.embeds[self.current_embed].timeout()
        if isinstance(self.message, discord.InteractionMessage):
            await self.message.edit(embed=self.embeds[self.current_embed], view=self)

    def disable_buttons(self) -> None:
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

    async def timeout_after(self, seconds: float):
        await asyncio.sleep(seconds)
        self.stop()
        await self.on_timeout()

async def send_movedex_view(interaction: discord.Interaction, move: PokemonMove, timeout: float = 180):
    view = MovedexView(move=move, user_id=interaction.user.id)
    await view._generate_embeds()
    await interaction.followup.send(embed=view.embeds["general"], view=view)
    view.message = await interaction.original_response()
    await view.timeout_after(timeout)