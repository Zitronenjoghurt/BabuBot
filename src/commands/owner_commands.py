from discord.ext import commands
from src.entities.user import User

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Application commands synced.")

    @commands.command()
    @commands.is_owner()
    async def entry(self, ctx: commands.Context, id: str):
        user = User.find(userid=id)
        if not isinstance(user, User):
            await ctx.send("User not found.")
        message = f"```json\n{user.to_json_string()}\n```"
        await ctx.reply(message)

    @commands.command()
    @commands.is_owner()
    async def reset_user_profile(self, ctx: commands.Context, id: str):
        user = User.find(userid=id)
        if not isinstance(user, User):
            await ctx.send("User not found.")
        user.profile.clear()
        user.save()
        await ctx.reply("User profile cleared.")

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))