import discord
from src.apis.abstract_api_controller import AbstractApiController

# Just used as an interface class for streamlining multiple apis into one command
class AbstractEmbedApi(AbstractApiController):
    async def generate_embed(self) -> discord.Embed:
        return discord.Embed()