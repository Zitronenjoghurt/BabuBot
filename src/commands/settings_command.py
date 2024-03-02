import discord
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.entities.user import User

CONFIG = Config.get_instance()

class SettingsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="settings", description="Adjust various settings for the fishing game")
    @app_commands.describe(ai_responses="The bot can use your messages for ai generated responses")
    async def settings(self, interaction: discord.Interaction, ai_responses: Optional[bool] = None):
        user: User = await User.load(userid=str(interaction.user.id))
        updated = user.settings.update(ai_responses=ai_responses)
        await user.save()

        if not updated:
            embed = discord.Embed(title="SETTINGS", color=discord.Color.light_grey())
        else:
            embed = discord.Embed(title="SETTINGS UPDATED", color=discord.Color.green())
        for setting, state in user.settings.get_fields():
            embed.add_field(name=setting, value=state, inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SettingsCommand(bot))