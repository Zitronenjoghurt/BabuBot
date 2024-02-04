import discord
from discord import app_commands
from discord.ext import commands
from src.logging.logger import LOGGER

class CommmandEvents(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command|app_commands.ContextMenu):
        LOGGER.debug(f"Command {command.name} by {interaction.user.name} ({interaction.user.id}) was successfully executed")

async def setup(bot):
    await bot.add_cog(CommmandEvents(bot))