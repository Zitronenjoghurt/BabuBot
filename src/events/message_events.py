import discord
from discord.ext import commands
from src.constants.config import Config
from src.entities.user import User
from src.entities.word_analyzer import WordAnalyzer

CONFIG = Config.get_instance()

class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        content = message.content
        if len(content) == 0:
            return
        
        # Check if message channel is an ignored channel
        channel_id = message.channel.id
        if channel_id:
            if int(channel_id) in CONFIG.IGNORED_CHANNEL_IDS:
                return
        
        for word in content.split(" "):
            if word.lower() in CONFIG.IGNORED_MESSAGE_WORDS:
                return

        author_id = str(message.author.id)
        user: User = await User.load(userid=author_id)
        word_analyzer: WordAnalyzer = await WordAnalyzer.load(userid=author_id)

        user.levels.gain()
        user.message_statistics.process_message(message=content)

        for word in content.split(" "):
            word = word.lower().strip()
            if word in CONFIG.COUNTED_WORDS:
                user.word_counter.count_word(word=word)
            word_analyzer.process_word(word=word)

        await user.cache_member_data(bot=self.bot)

        await user.save()
        await word_analyzer.save()

async def setup(bot):
    await bot.add_cog(MessageEvents(bot))