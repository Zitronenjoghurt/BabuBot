import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.custom_embeds import ErrorEmbed
from src.entities.pokemon.pokemon import Pokemon
from src.ui.pokedex_view import send_pokedex_view

class PokemonCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="pokedex", description="Get all important information about a pokemon.")
    @app_commands.describe(name="Name of the pokemon in en, de or fr. Can include typos.")
    @app_commands.checks.cooldown(1, 5)
    async def pokdedex(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        pokemon = await Pokemon.fetch(pokemon_name=name)
        if not isinstance(pokemon, Pokemon):
            return await interaction.followup.send(embed=ErrorEmbed(title="Pokemon not found", message="The specified pokemon does not exist. The typo-correction only recognizes en, de and fr pokemon names."))
        
        await send_pokedex_view(interaction=interaction, pokemon=pokemon)

async def setup(bot: commands.Bot):
    await bot.add_cog(PokemonCommands(bot))