import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.fishing.fish_library import FishEntry, FishLibrary
from src.logging.logger import LOGGER

CONFIG = Config.get_instance()
FISH_LIBRARY = FishLibrary.get_instance()

class FishingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="fish", description="Fish for some random fish of random rarity!")
    async def tasks(self, interaction: discord.Interaction):
        user: User = await User.load(userid=str(interaction.user.id))
        if not user.fishing.unlocked:
            return await interaction.response.send_message(embed=ErrorEmbed(title="YOU HAVE NO FISHING ROD", message="Look in the shop at `/shop rods` or buy the regular rod directly via `/buy R1` or `/buy Regular Rod` to get going!"), ephemeral=True)
        
        rod_level = user.fishing.rod_level
        bait_level = 0

        fish_entry = FISH_LIBRARY.random_fish_entry(rod_level=rod_level, bait_level=bait_level)
        if not isinstance(fish_entry, FishEntry):
            LOGGER.error(f"Unable to retrieve random fish entry, received: {fish_entry}")
            return await interaction.response.send_message(embed=ErrorEmbed(title="AN ERROR OCCURED", message="An error occured while selecting a random fish, please contact the developer."), ephemeral=True)
        
        user.fishing.process_fish(fish_entry=fish_entry)
        await user.save()

async def setup(bot):
    await bot.add_cog(FishingCommands(bot))