import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.scrollables.level_top_scrollable import LevelTopScrollable
from src.ui.scrollable_embed import ScrollableEmbed
from src.utils.interaction_operations import send_scrollable

CONFIG = Config.get_instance()

class LevelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="level", description=f"Look up your current level")
    @app_commands.describe(member="The user you want to check the level of")
    async def level(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        if member:
            if member.bot:
                return await interaction.response.send_message(embed=ErrorEmbed(title=f"ERROR", message="Bots do not gain xp."))
            target = member
            userid = str(member.id)
        else:
            target = interaction.user
            userid = str(interaction.user.id)

        user: User = await User.load(userid=userid)

        current_level = user.levels.get_level()
        progress_bar, progress_ratio = user.levels.get_level_progress()
        gained_xp, needed_xp = user.levels.get_xp_progress()

        embed = discord.Embed(
            title="LEVEL",
            color=target.color,
            timestamp=datetime.now()
        )
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        embed.add_field(name="CURRENT LEVEL", value=f"**`{current_level}`**", inline=False)
        embed.add_field(name="PROGRESS", value=f"**`{gained_xp}/{needed_xp}XP ({round(progress_ratio*100, CONFIG.DECIMAL_DIGITS)}%)`**\n{progress_bar}", inline=False)
        embed.add_field(name="TOTAL XP", value=f"**`{user.levels.total_xp}`**")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="level-toplist", description=f"Look up the level toplist")
    async def level_toplist(self, interaction: discord.Interaction):
        scrollable = await LevelTopScrollable.create()
        embed = ScrollableEmbed(
            scrollable=scrollable,
            title="LEVEL TOPLIST",
            color=discord.Color.from_str("#FFFFFF")
        )
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(LevelCommands(bot))