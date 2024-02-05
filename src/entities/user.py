import discord
from datetime import datetime
from discord.ext import commands
from typing import Optional
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.economy import Economy
from src.entities.message_statistics import MessageStatistics
from src.entities.profile import Profile
from src.entities.word_counter_toplist import WordCounterToplist
from src.entities.word_counter import WordCounter
from src.utils.dict_operations import sort_simple
from src.utils.validator import validate_of_type

class User(AbstractDatabaseEntity):
    TABLE_NAME = "users"
    SERIALIZED_PROPERTIES = ["id", "userid", "created_stamp", "message_statistics", "word_counter", "profile", "economy"]
    SERIALIZE_CLASSES = {"word_counter": WordCounter, "message_statistics": MessageStatistics, "profile": Profile, "economy": Economy}
    SAVED_PROPERTIES = ["userid", "created_stamp", "message_statistics", "word_counter", "profile", "economy"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            userid: Optional[str] = None,
            message_statistics: Optional[MessageStatistics] = None,
            word_counter: Optional[WordCounter] = None,
            profile: Optional[Profile] = None,
            economy: Optional[Economy] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        if userid is None:
            userid = ""
        if message_statistics is None:
            message_statistics = MessageStatistics()
        if word_counter is None:
            word_counter = WordCounter()
        if profile is None:
            profile = Profile()
        if economy is None:
            economy = Economy()

        validate_of_type(message_statistics, MessageStatistics, "message_statistics")
        validate_of_type(word_counter, WordCounter, "word_counter")
        validate_of_type(profile, Profile, "profile")
        validate_of_type(economy, Economy, "economy")

        self.userid = str(userid)
        self.message_statistics: MessageStatistics = message_statistics
        self.word_counter: WordCounter = word_counter
        self.profile: Profile = profile
        self.economy: Economy = economy
        
    @staticmethod
    def global_word_count() -> WordCounter:
        users: list[User] = User.findall()
        word_counter = WordCounter.accumulate([user.word_counter for user in users if isinstance(user.word_counter, WordCounter)])
        return word_counter
    
    @staticmethod
    def global_word_toplist() -> WordCounterToplist:
        users: list[User] = User.findall()
        toplist: dict[str, dict[str, int]] = {}
        for user in users:
            for word, count in user.word_counter.words.items():
                if word not in toplist:
                    toplist[word] = {}
                toplist[word][user.userid] = count
        
        sorted_toplist: dict[str, dict[str, int]] = {}
        for word, data in toplist.items():
            sorted_toplist[word] = sort_simple(data=data, descending=True)

        return WordCounterToplist(sorted_toplist)

    async def fetch_discord_user(self, bot: commands.Bot) -> Optional[discord.User]:
        user = await bot.fetch_user(int(self.userid))
        return user
    
    def get_created_time(self) -> datetime:
        return datetime.fromtimestamp(self.created_stamp)