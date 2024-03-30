import asyncio
import discord
from discord.ui import Button, View
from typing import Optional
from src.constants.emoji_index import EmojiIndex
from src.entities.pokemon.pokemon import Pokemon, PokedexEmbed

EMOJI_INDEX = EmojiIndex.get_instance()

class PokedexView(View):
    def __init__(self, pokemon: Pokemon, user_id: int, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.pokemon = pokemon
        self.user_id = user_id
        self.embeds: dict[str, PokedexEmbed] = self.generate_embeds()
        self.current_embed = "general"

        self.message: Optional[discord.InteractionMessage] = None

    def generate_embeds(self) -> dict[str, PokedexEmbed]:
        embeds = {}
        embeds["general"] = self.pokemon.generate_general_embed()
        embeds["weakness"] = self.pokemon.generate_weakness_embed()
        embeds["stats"] = self.pokemon.generate_base_stats_embed()
        return embeds

    @discord.ui.button(emoji="✨", style=discord.ButtonStyle.red)
    async def shiny_button(self, interaction: discord.Interaction, button: Button):
        self.toggle_shiny()
        await interaction.response.edit_message(embed=self.embeds[self.current_embed])

    @discord.ui.button(emoji="ℹ️", style=discord.ButtonStyle.primary)
    async def general_button(self, interaction: discord.Interaction, button: Button):
        self.current_embed = "general"
        await interaction.response.edit_message(embed=self.embeds["general"])

    @discord.ui.button(emoji="⚔", style=discord.ButtonStyle.secondary)
    async def weakness_button(self, interaction: discord.Interaction, button: Button):
        self.current_embed = "weakness"
        await interaction.response.edit_message(embed=self.embeds["weakness"])

    @discord.ui.button(emoji=EMOJI_INDEX.get_emoji("base_stats"), style=discord.ButtonStyle.secondary)
    async def stats_button(self, interaction: discord.Interaction, button: Button):
        self.current_embed = "stats"
        await interaction.response.edit_message(embed=self.embeds["stats"])
    
    def toggle_shiny(self) -> None:
        for embed in self.embeds.values():
            embed.toggle_shiny()

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

async def send_pokedex_view(interaction: discord.Interaction, pokemon: Pokemon, timeout: float = 180):
    view = PokedexView(pokemon=pokemon, user_id=interaction.user.id)
    stats_image_file = pokemon.stats_image.get_image_file()
    await interaction.followup.send(embed=view.embeds["general"], view=view, file=stats_image_file)
    view.message = await interaction.original_response()
    await view.timeout_after(timeout)