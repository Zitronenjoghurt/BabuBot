import discord
from discord import app_commands
from discord.ext import commands
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.ui.feedback_modal import FeedbackModal

class FeedbackCommand(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="feedback", description="If you want to provide feedback (5 minute cooldown)")
    @app_commands.checks.cooldown(1, 300)
    async def feedback(self, interaction: discord.Interaction):
        user: User = await User.load(userid=str(interaction.user.id))
        await interaction.response.send_modal(FeedbackModal(user))
    
    @feedback.error
    async def on_feedback_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        await interaction.response.send_message(embed=ErrorEmbed(title="ERROR", message=str(error)), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(FeedbackCommand(bot))