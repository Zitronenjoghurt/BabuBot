import discord
from discord.ext import commands
from src.constants.config import Config
from src.entities.user import User

CONFIG = Config.get_instance()

class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        user: User = User.load(userid=str(message.author.id))

        counted_words = CONFIG.countable_words_in_message(message=message.content)
        for word in counted_words:
            user.word_counter.count_word(word=word)

        user.save()

async def setup(bot):
    await bot.add_cog(MessageEvents(bot))