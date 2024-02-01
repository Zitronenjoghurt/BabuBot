from discord.ext import commands

class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.hybrid_command()
    async def ping(self, ctx):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"**Pong!** {latency_ms}ms\nI'll just be staying online this night as a test!")

async def setup(bot):
    await bot.add_cog(MiscCommands(bot))