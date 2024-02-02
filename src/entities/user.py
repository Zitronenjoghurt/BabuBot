import discord
from datetime import datetime
from discord.ext import commands
from typing import Optional
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.message_statistics import MessageStatistics
from src.entities.profile import Profile
from src.entities.word_counter import WordCounter
from src.utils.validator import validate_of_type

class User(AbstractDatabaseEntity):
    TABLE_NAME = "users"
    SERIALIZED_PROPERTIES = ["id", "userid", "created_stamp", "message_statistics", "word_counter", "profile"]
    SERIALIZE_CLASSES = {"word_counter": WordCounter, "message_statistics": MessageStatistics, "profile": Profile}
    SAVED_PROPERTIES = ["userid", "created_stamp", "message_statistics", "word_counter", "profile"]

    def __init__(
            self, 
            id: Optional[int] = None, 
            userid: Optional[str] = None, 
            created_stamp: Optional[float] = None,
            message_statistics: Optional[MessageStatistics] = None,
            word_counter: Optional[WordCounter] = None,
            profile: Optional[Profile] = None
        ) -> None:
        super().__init__(id=id)
        if userid is None:
            userid = ""
        if created_stamp is None:
            created_stamp = datetime.now().timestamp()
        if message_statistics is None:
            message_statistics = MessageStatistics()
        if word_counter is None:
            word_counter = WordCounter()
        if profile is None:
            profile = Profile()

        validate_of_type(message_statistics, MessageStatistics, "message_statistics")
        validate_of_type(word_counter, WordCounter, "word_counter")
        validate_of_type(profile, Profile, "profile")

        self.userid = str(userid)
        self.created_stamp = float(created_stamp)
        self.message_statistics: MessageStatistics = message_statistics
        self.word_counter: WordCounter = word_counter
        self.profile: Profile = profile

    async def fetch_discord_user(self, bot: commands.Bot) -> Optional[discord.User]:
        user = await bot.fetch_user(int(self.userid))
        return user