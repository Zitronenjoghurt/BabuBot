import discord
from discord import app_commands
from discord.ext import commands
from src.constants.config import Config
from src.entities.user import User
from typing import Optional
from src.ui.profile_modal import ProfileModal
from src.utils.bot_operations import retrieve_guild_strict
from src.utils.guild_operations import retrieve_member_strict

CONFIG = Config.get_instance()

class ProfileCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    profile_group = app_commands.Group(name="profile", description="All commands about user profiles")

    @profile_group.command(name="show", description="Will show you your server profile")
    @app_commands.describe(member="The user you want to see the profile of")
    async def profile_show(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if isinstance(member, discord.Member):
            user_id = member.id
            count_view = user_id != interaction.user.id
        else:
            user_id = interaction.user.id
            guild = await retrieve_guild_strict(self.bot, CONFIG.GUILD_ID)
            member = await retrieve_member_strict(guild=guild, member_id=user_id)
            count_view = False
        
        user: User = await User.load(userid=str(user_id))
        if count_view:
            user.profile.count_view()
            await user.save()

        embed = generate_profile_embed(user=user, member=member)

        await interaction.response.send_message(embed=embed)

    @profile_group.command(name="change", description="Opens a pop-up for changing your server profile")
    async def profile_change(self, interaction: discord.Interaction):
        user: User = await User.load(userid=str(interaction.user.id))
        await interaction.response.send_modal(ProfileModal(user))
    
def generate_profile_embed(user: User, member: discord.Member) -> discord.Embed:
    embed = discord.Embed(
        color=member.color
    )
    embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    embed.set_footer(text=f"views: {str(user.profile.views)}")

    # Add profile fields
    fields = user.profile.generate_fields()
    if len(fields) == 0:
        embed.description = "*This user has not set their profile yet.*"
    else:
        for field in fields:
            embed.add_field(**field)

    # Add other fields
    embed.add_field(name="REP RECEIVED/GIVEN", value=f"**`{user.reputation.points_received}/{user.reputation.points_given}`**")

    return embed

async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCommands(bot))