import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User

class FishingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="fish", description="Fish for some random fish of random rarity!")
    async def tasks(self, interaction: discord.Interaction):
        user: User = await User.load(userid=str(interaction.user.id))
        if not user.fishing.unlocked:
            return await interaction.response.send_message(embed=ErrorEmbed(title="YOU HAVE NO FISHING ROD", message="Look in the shop at `/shop rods` or buy the regular rod directly via `/buy R1` or `/buy Regular Rod` to get going!"), ephemeral=True)
        
        await interaction.response.send_message(content="Fish")

async def setup(bot):
    await bot.add_cog(FishingCommands(bot))