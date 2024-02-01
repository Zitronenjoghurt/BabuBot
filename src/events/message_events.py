import discord
from discord.ext import commands
from src.entities.user import User

class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        user: User = User.load(userid=str(message.author.id))
        user.count_message()
        user.save()

async def setup(bot):
    await bot.add_cog(MessageEvents(bot))