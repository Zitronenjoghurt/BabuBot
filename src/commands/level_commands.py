import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.entities.user import User

CONFIG = Config.get_instance()

class LevelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="level", description=f"Look up your current level")
    @app_commands.describe(member="The user you want to check the level of")
    async def daily(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        if member:
            target = member
            userid = str(member.id)
        else:
            target = interaction.user
            userid = str(interaction.user.id)

        user: User = await User.load(userid=userid)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(LevelCommands(bot))