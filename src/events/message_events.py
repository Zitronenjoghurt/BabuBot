import asyncio
import discord
import random
from discord.ext import commands
from src.apis.openai_api import OpenAIApi
from src.constants.config import Config
from src.entities.user import User
from src.entities.word_analyzer import WordAnalyzer
from src.logging.channel_logger import ChannelLogger
from src.logging.logger import LOGGER

CHANNEL_LOGGER = ChannelLogger.get_instance()
CONFIG = Config.get_instance()

OPENAI = OpenAIApi.get_instance()

class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if isinstance(message.channel, discord.DMChannel):
            LOGGER.info(f"Received DM message from {message.author.name} ({message.author.id}): {message.content}")
            await CHANNEL_LOGGER.dm(message=message)
        
        if not isinstance(message.channel, discord.TextChannel):
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

        should_respond = random.randint(1, 100) == 69
        if should_respond:
            asyncio.create_task(ai_answer(message=message, user=user))

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

async def ai_answer(message: discord.Message, user: User) -> None:
    username = message.author.display_name
    pronouns = user.profile.pronouns

    name = username if len(pronouns) == 0 else username + f" ({pronouns})"
    prompt = f"{name}\n{message.content}"

    answer = await OPENAI.request(preset_name='message_commenter', user_message=prompt)
    if answer:
        await message.reply(content=answer)

async def setup(bot):
    await bot.add_cog(MessageEvents(bot))