import discord
from discord.ext import commands
from src.constants.config import Config
from src.entities.user import User
from src.logging.logger import LOGGER

CONFIG = Config.get_instance()

class MemberEvents(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.bot:
            return
        
        LOGGER.debug(f"Detected member update ({after.id}), syncing database member cache")

        user: User = User.find(userid=str(before.id))
        await user.cache_member_data(self.bot, after)
        user.save()

async def setup(bot):
    await bot.add_cog(MemberEvents(bot))