import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.custom_embeds import ErrorEmbed
from src.pokemon.game_versions import PokemonGameVersions, PokemonVersionGroup
from src.pokemon.names import PokemonNames
from src.entities.pokemon.pokemon import Pokemon
from src.ui.pokedex_view import send_pokedex_view

PN = PokemonNames.get_instance()
GAME_VERSIONS = PokemonGameVersions.get_instance()

class PokemonCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="pokedex", description="Get all important information about a pokemon.")
    @app_commands.describe(name="Name of the pokemon. Can include typos.")
    @app_commands.describe(version="Game version for version-specific data.")
    @app_commands.checks.cooldown(1, 5)
    async def pokdedex(self, interaction: discord.Interaction, name: str, version: Optional[str] = None):
        await interaction.response.defer()

        pokemon = await Pokemon.fetch(pokemon_name=name)
        if not isinstance(pokemon, Pokemon):
            return await interaction.followup.send(embed=ErrorEmbed(title="Pokemon not found", message="The specified pokemon does not exist. The typo-correction only recognizes en, de and fr pokemon names."))
        
        version_id = None
        if version:
            version_group = GAME_VERSIONS.get_by_name(name=version)
            if isinstance(version_group, PokemonVersionGroup):
                version_id = version_group.id

        await send_pokedex_view(interaction=interaction, pokemon=pokemon, version_id=version_id)

    @app_commands.command(name="pokemon-name", description="Find the closest pokemon name to your provided name.")
    @app_commands.describe(name="Name of the pokemon. Can include typos.")
    @app_commands.checks.cooldown(1, 5)
    async def pokemon_name(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        result = PN.match_name_extended(name=name)
        if result is None:
            return await interaction.followup.send(embed=ErrorEmbed(title="Pokemon not found", message="The provided name does not match any pokemon name in the slightest."))
        
        final_name, matched_name, score = result

        match = matched_name.capitalize()
        final = format_name(final_name)

        description = ""
        if match != final:
            description = f"*matched from* **`{match}`**\n"
        description += f"Confidence: **`{score}%`**"

        embed = discord.Embed(
            title=final,
            description=description,
            color=discord.Color.from_str("#74F2C8")
        )
        embed.set_author(name="POKEMON NAME GUESS")
        await interaction.followup.send(embed=embed)

    @pokdedex.autocomplete("version")
    async def game_version_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=version_choice, value=version_choice)
            for version_choice in GAME_VERSIONS.versions
            if current.lower() in version_choice.lower()
        ]

def format_name(name: str) -> str:
    words = name.replace('-', ' ').split()
    return ' '.join(word.capitalize() for word in words)

async def setup(bot: commands.Bot):
    await bot.add_cog(PokemonCommands(bot))