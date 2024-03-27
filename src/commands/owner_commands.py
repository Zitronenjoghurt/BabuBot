import discord
from discord.ext import commands
from src.entities.user import User
from src.logging.logger import LOGGER
from src.utils.bot_operations import notify_user_private

class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def notify(self, ctx, member: discord.Member, *, text: str):
        if not isinstance(member, discord.Member):
            return
        success = await notify_user_private(bot=self.bot, user_id=member.id, message=text)
        if success:
            await ctx.send("Notified user.")
        else:
            await ctx.send("Unable to notify user.")

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Application commands synced.")
        LOGGER.info("Synced application commands")

    @commands.command()
    @commands.is_owner()
    async def reset_user_profile(self, ctx: commands.Context, id: str):
        user = await User.find(userid=id)
        if not isinstance(user, User):
            await ctx.send("User not found.")
        user.profile.clear()
        await user.save()
        await ctx.reply("User profile cleared.")
        LOGGER.info(f"Cleared user profile of {user.get_name()} ({id})")

    @commands.command()
    @commands.is_owner()
    async def enable(self, ctx: commands.Context, id: str):
        user = await User.find(userid=id)
        if not isinstance(user, User):
            await ctx.send("User not found.")
        user.settings.ai_responses = True
        await user.save()
        await ctx.reply("User ai answers enabled.")
        LOGGER.info(f"AI answers for user {user.get_name()} ({id}) were enabled")

    @commands.command()
    @commands.is_owner()
    async def disable_ai(self, ctx: commands.Context, id: str):
        user = await User.find(userid=id)
        if not isinstance(user, User):
            await ctx.send("User not found.")
        user.settings.ai_responses = False
        await user.save()
        await ctx.reply("User ai answers disabled.")
        LOGGER.info(f"AI answers for user {user.get_name()} ({id}) were disabled")

async def setup(bot):
    await bot.add_cog(OwnerCommands(bot))