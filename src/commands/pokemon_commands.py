import discord
from discord import app_commands
from discord.ext import commands
from src.constants.custom_embeds import ErrorEmbed
from src.constants.pokemon_names import PokemonNames
from src.entities.pokemon.pokemon import Pokemon
from src.ui.pokedex_view import send_pokedex_view

PN = PokemonNames.get_instance()

class PokemonCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="pokedex", description="Get all important information about a pokemon.")
    @app_commands.describe(name="Name of the pokemon. Can include typos.")
    @app_commands.checks.cooldown(1, 5)
    async def pokdedex(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()

        pokemon = await Pokemon.fetch(pokemon_name=name)
        if not isinstance(pokemon, Pokemon):
            return await interaction.followup.send(embed=ErrorEmbed(title="Pokemon not found", message="The specified pokemon does not exist. The typo-correction only recognizes en, de and fr pokemon names."))
        
        await send_pokedex_view(interaction=interaction, pokemon=pokemon)

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

def format_name(name: str) -> str:
    words = name.replace('-', ' ').split()
    return ' '.join(word.capitalize() for word in words)

async def setup(bot: commands.Bot):
    await bot.add_cog(PokemonCommands(bot))