from discord.ext import commands

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.hybrid_command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))