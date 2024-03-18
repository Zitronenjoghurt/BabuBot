import discord
from discord import app_commands
from discord.ext import commands
from src.constants.custom_embeds import ErrorEmbed
from src.apis.lemon_image_api import LemonImageApi, ApiError, CATEGORIES, CATEGORY_VERB, CATEGORY_COLOR

LIA = LemonImageApi.get_instance()

class ActionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="action", description="Perform various actions on users of the server")
    @app_commands.describe(action="The action you want to take")
    @app_commands.describe(member="The target of the action youre taking")
    async def action(self, interaction: discord.Interaction, action: str, member: discord.Member):
        if member.id == interaction.user.id:
            return await interaction.response.send_message(embed=ErrorEmbed(title="Really?", message="You really want to do this to yourself? I cant even get myself to feel pity, holy..."), ephemeral=True)
        action = action.lower()
        if action not in CATEGORIES:
            return await interaction.response.send_message(embed=ErrorEmbed(title="ACTION NOT FOUND", message="The provided action does not exist."), ephemeral=True)
        
        await interaction.response.defer()

        try:
            image_url = await LIA.random_image(category=action)
        except ApiError as e:
            return await interaction.followup.send(embed=ErrorEmbed(title="AN ERROR OCCURED", message=f"{e}"))
        
        embed = discord.Embed(
            title=f"{interaction.user.display_name} {CATEGORY_VERB[action]} {member.display_name}",
            color=discord.Color.from_str(CATEGORY_COLOR[action])
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"{LIA.category_counts[action]} {action} images provided by api.lemon.industries")
        embed.set_image(url=image_url)
        await interaction.followup.send(content=f"<@{member.id}>", embed=embed)

    @action.autocomplete("action")
    async def action_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=action_choice, value=action_choice)
            for action_choice in CATEGORIES
            if current.lower() in action_choice.lower()
        ]

async def setup(bot: commands.Bot):
    await bot.add_cog(ActionCommand(bot))