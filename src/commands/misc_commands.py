import discord
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.utils.bot_operations import retrieve_guild_strict
from src.utils.guild_operations import retrieve_member_strict

CONFIG = Config.get_instance()

class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.hybrid_command()
    async def ping(self, ctx):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"**Pong!** {latency_ms}ms\n")

    @app_commands.command(name="tasks", description="Will show you your daily and overall tasks")
    @app_commands.describe(member="The user you want to see the tasks of")
    async def tasks(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if isinstance(member, discord.Member):
            if member.bot:
                return await interaction.response.send_message(embed=ErrorEmbed(title=f"ERROR", message="Bots do not do tasks."))
            user_id = member.id
        else:
            user_id = interaction.user.id
            guild = await retrieve_guild_strict(self.bot, CONFIG.GUILD_ID)
            member = await retrieve_member_strict(guild=guild, member_id=user_id)

        user: User = await User.load(userid=str(user_id))
        tasks = await user.get_tasks()
        daily_tasks = user.get_daily_tasks()

        embed = discord.Embed(title="TASKS", description=generate_tasks_string(tasks), color=discord.Color.from_str("#ae53fc"), timestamp=datetime.now())
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.add_field(name="DAILY TASKS", value=generate_daily_tasks_string(daily_tasks), inline=False)
        embed.add_field(name="COOLDOWNS", value=user.get_cooldowns(), inline=False)
        embed.add_field(name="OTHER THINGS", value="`Dont forget your relationships!`\n`Dont forget to go fish with /fish!`", inline=False)
        embed.set_footer(text="Also try out other commands, you can easily navigate them by typing a / in chat!")
        await interaction.response.send_message(embed=embed)

def generate_tasks_string(tasks: list[str]) -> str:
    if not tasks:
        return "*You did all available tasks!*"
    return "\n".join([f"❥ `{task}`" for task in tasks])

def generate_daily_tasks_string(tasks: list[tuple[str, bool]]) -> str:
    task_strings = []
    for task, state in tasks:
        symbol = "✅" if state else "❌"
        task_strings.append(f"{symbol} **`{task}`**")
    return "\n".join(task_strings)

async def setup(bot):
    await bot.add_cog(MiscCommands(bot))