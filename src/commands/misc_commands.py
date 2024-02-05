import discord
from discord import app_commands
from discord.ext import commands

class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.hybrid_command()
    async def ping(self, ctx):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"**Pong!** {latency_ms}ms\n")

    @app_commands.command(name="say", description="Will just repeat whatever you want to say")
    @app_commands.describe(message="Whatever message you want the bot to say")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(f"{message}")

async def setup(bot):
    await bot.add_cog(MiscCommands(bot))