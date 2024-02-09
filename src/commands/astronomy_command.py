import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.custom_embeds import ErrorEmbed
from src.apis.nasa_api import NasaApi, ApiError

NASA = NasaApi.get_instance()

class AstronomyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="astronomy", description="Display a random Astronomy Picture Of The Day from NASA")
    @app_commands.describe(private="If the response should be only visible to you")
    async def reputation(self, interaction: discord.Interaction, private: Optional[bool] = None):
        if private is None:
            private = False
        
        await interaction.response.defer(ephemeral=private)

        try:
            apod = await NASA.random_apod()
        except ApiError as e:
            return await interaction.followup.send(embed=ErrorEmbed(title="API ERROR", message=str(e)))
        
        embed = discord.Embed(
            title=apod.title,
            description=apod.description,
            color=discord.Color.from_str("#0b3d91")
        )
        embed.set_author(name="Random Astronomy Picture Of the Day", icon_url="https://api.nasa.gov/assets/img/favicons/favicon-192.png", url="https://apod.nasa.gov/apod/astropix.html")
        embed.set_image(url=apod.url)
        embed.set_footer(text=f"Date: {apod.date} | Copyright: {apod.copyright}")
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AstronomyCommand(bot))