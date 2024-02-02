import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.entities.user import User
from src.utils.discord_time import relative_time

CONFIG = Config.get_instance()

class StatisticsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    profile_group = app_commands.Group(name="stats", description="All commands about user profiles")

    @profile_group.command(name="messages", description="Provides message statistics")
    @app_commands.describe(member="The user you want to see the message statistics of")
    async def messages(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if isinstance(member, discord.Member):
            user_id = member.id
        else:
            user_id = interaction.user.id
            guild = await self.bot.fetch_guild(CONFIG.GUILD_ID)
            member = await guild.fetch_member(user_id)
        
        user: User = User.load(userid=str(user_id))

        message_count = user.message_statistics.message_count
        total_characters = user.message_statistics.total_characters
        average_length = round(total_characters/message_count, CONFIG.DECIMAL_DIGITS)

        embed = discord.Embed(title="MESSAGE STATISTICS", color=discord.Color.from_str("#FFFFFF"))
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.add_field(name="Analyzed since", value=relative_time(int(user.created_stamp)))
        embed.add_field(name="Total message count", value=f"`{message_count}`", inline=True)
        embed.add_field(name="Total character count", value=f"`{total_characters}`", inline=True)
        embed.add_field(name="Average message length", value=f"`{average_length}`", inline=True)
        await interaction.response.send_message(embed=embed)

    @profile_group.command(name="words", description="Provides statistics about said words")
    @app_commands.describe(member="The user you want to see the word statistics of")
    async def words(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if isinstance(member, discord.Member):
            user_id = member.id
        else:
            user_id = interaction.user.id
            guild = await self.bot.fetch_guild(CONFIG.GUILD_ID)
            member = await guild.fetch_member(user_id)
        
        user: User = User.load(userid=str(user_id))
        toplist = user.global_word_toplist()
        positions = toplist.get_positions(user_id=user.userid)

        embed = discord.Embed(title="WORD STATISTICS", color=discord.Color.from_str("#FFFFFF"))
        embed.description = user.word_counter.to_string_with_positions(positions=positions)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.add_field(name="Analyzed since", value=relative_time(int(user.created_stamp)))
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(StatisticsCommands(bot))