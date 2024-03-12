import discord
import random
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.custom_embeds import ErrorEmbed
from src.apis.abstract_embed_api import AbstractEmbedApi
from src.apis.random_cat_api import RandomCatApi
from src.apis.random_dog_api import ApiError, RandomDogApi
from src.apis.random_duck_api import RandomDuckApi

RANDOM_CAT = RandomCatApi.get_instance()
RANDOM_DOG = RandomDogApi.get_instance()
RANDOM_DUCK = RandomDuckApi.get_instance()

APIS = [RANDOM_CAT, RANDOM_DOG, RANDOM_DUCK]

class PetCommand(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="pet", description="Get a random image of a pet")
    @app_commands.describe(private="If the response should be only visible to you")
    @app_commands.checks.cooldown(1, 5)
    async def pet(self, interaction: discord.Interaction, private: Optional[bool] = None):
        if private is None:
            private = False
        await interaction.response.defer(ephemeral=private)
        try:
            api = select_api()
            embed = await api.generate_embed()
        except ApiError as e:
            return await interaction.followup.send(embed=ErrorEmbed(title="API ERROR", message=str(e)))
        await interaction.followup.send(embed=embed)

def select_api() -> AbstractEmbedApi:
    return random.choice(APIS)

async def setup(bot: commands.Bot):
    await bot.add_cog(PetCommand(bot))