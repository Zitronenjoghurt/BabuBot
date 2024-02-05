import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.utils.bot_operations import retrieve_guild_strict
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
            guild = await retrieve_guild_strict(self.bot, CONFIG.GUILD_ID)
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
            guild = await retrieve_guild_strict(self.bot, CONFIG.GUILD_ID)
            member = await guild.fetch_member(user_id)
        
        user: User = User.load(userid=str(user_id))
        toplist = User.global_word_toplist()
        positions = toplist.get_positions(user_id=user.userid)

        embed = discord.Embed(title="WORD STATISTICS", color=discord.Color.from_str("#FFFFFF"))
        embed.description = user.word_counter.to_string_with_positions(positions=positions)
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.add_field(name="Analyzed since", value=relative_time(int(user.created_stamp)))
        await interaction.response.send_message(embed=embed)

    @profile_group.command(name="words-total", description="Provides statistics about the total count of all tracked words")
    async def words_total(self, interaction: discord.Interaction):
        word_count = User.global_word_count()

        embed = discord.Embed(title="TOTAL WORD STATISTICS", color=discord.Color.from_str("#FFFFFF"))
        embed.description = str(word_count)
        await interaction.response.send_message(embed=embed)

    @profile_group.command(name="words-toplist", description="Provides a toplist about who said a certain tracked word the most")
    @app_commands.describe(word="The word you want to see the toplist of")
    async def words_toplist(self, interaction: discord.Interaction, word: str):
        if not isinstance(word, str):
            await interaction.response.send_message(embed=ErrorEmbed(title="INVALID WORD", message="Please provide a WORD, just a regular word..."), ephemeral=True)
            return
        
        word = word.lower()
        if word not in CONFIG.COUNTED_WORDS:
            await interaction.response.send_message(embed=ErrorEmbed(title="WORD DOES NOT EXIST", message=f"The provided word is not in the list of tracked words."), ephemeral=True)
            return
        
        guild = await retrieve_guild_strict(self.bot, CONFIG.GUILD_ID)
        
        toplist = User.global_word_toplist()

        embed = discord.Embed(title=f"{word.upper()} TOPLIST", color=discord.Color.from_str("#FFFFFF"))
        embed.description = await toplist.get_word_positions_string(guild=guild, word=word, maximum=20)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(StatisticsCommands(bot))