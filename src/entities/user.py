import discord
from datetime import datetime
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.economy import Economy
from src.entities.message_statistics import MessageStatistics
from src.entities.profile import Profile
from src.entities.relationship import Relationship
from src.entities.reputation import Reputation
from src.entities.word_counter_toplist import WordCounterToplist
from src.entities.word_counter import WordCounter
from src.logging.logger import LOGGER
from src.utils.bot_operations import retrieve_guild_strict
from src.utils.dict_operations import sort_simple
from src.utils.guild_operations import retrieve_member
from src.utils.validator import validate_of_type

CONFIG = Config.get_instance()

class User(AbstractDatabaseEntity):
    TABLE_NAME = "users"
    SERIALIZED_PROPERTIES = ["id", "userid", "created_stamp", "name", "display_name", "sent_feedback", "accepted_command_cost", "message_statistics", "word_counter", "profile", "economy", "reputation"]
    SERIALIZE_CLASSES = {"word_counter": WordCounter, "message_statistics": MessageStatistics, "profile": Profile, "economy": Economy, "reputation": Reputation}
    SAVED_PROPERTIES = ["userid", "created_stamp", "name", "display_name", "sent_feedback", "accepted_command_cost", "message_statistics", "word_counter", "profile", "economy", "reputation"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            userid: Optional[str] = None,
            name: Optional[str] = None,
            display_name: Optional[str] = None,
            sent_feedback: Optional[bool] = None,
            accepted_command_cost: Optional[list[str]] = None,
            message_statistics: Optional[MessageStatistics] = None,
            word_counter: Optional[WordCounter] = None,
            profile: Optional[Profile] = None,
            economy: Optional[Economy] = None,
            reputation: Optional[Reputation] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        if userid is None:
            userid = ""
        if name is None:
            name = ""
        if display_name is None:
            display_name = ""
        if sent_feedback is None:
            sent_feedback = False
        if accepted_command_cost is None:
            accepted_command_cost = []
        if message_statistics is None:
            message_statistics = MessageStatistics()
        if word_counter is None:
            word_counter = WordCounter()
        if profile is None:
            profile = Profile()
        if economy is None:
            economy = Economy()
        if reputation is None:
            reputation = Reputation()

        validate_of_type(message_statistics, MessageStatistics, "message_statistics")
        validate_of_type(word_counter, WordCounter, "word_counter")
        validate_of_type(profile, Profile, "profile")
        validate_of_type(economy, Economy, "economy")
        validate_of_type(reputation, Reputation, "reputation")

        self.userid = str(userid)
        self.name = name
        self.display_name = display_name
        self.sent_feedback = sent_feedback
        self.accepted_command_cost = accepted_command_cost
        self.message_statistics: MessageStatistics = message_statistics
        self.word_counter: WordCounter = word_counter
        self.profile: Profile = profile
        self.economy: Economy = economy
        self.reputation: Reputation = reputation
        
    @staticmethod
    async def global_word_count() -> WordCounter:
        users: list[User] = await User.findall()
        word_counter = WordCounter.accumulate([user.word_counter for user in users if isinstance(user.word_counter, WordCounter)])
        return word_counter
    
    @staticmethod
    async def global_message_count() -> MessageStatistics:
        users: list[User] = await User.findall()
        message_statistics = MessageStatistics.accumulate([user.message_statistics for user in users if isinstance(user.message_statistics, MessageStatistics)])
        return message_statistics
    
    @staticmethod
    async def global_word_toplist() -> WordCounterToplist:
        users: list[User] = await User.findall()
        toplist: dict[str, dict[str, int]] = {}
        for user in users:
            for word, count in user.word_counter.words.items():
                if word not in toplist:
                    toplist[word] = {}
                toplist[word][user.get_display_name()] = count
        
        sorted_toplist: dict[str, dict[str, int]] = {}
        for word, data in toplist.items():
            sorted_toplist[word] = sort_simple(data=data, descending=True)

        return WordCounterToplist(sorted_toplist)
    
    def get_created_time(self) -> datetime:
        return datetime.fromtimestamp(self.created_stamp)
    
    async def rep_user(self, user: 'User|str') -> None:
        if isinstance(user, str):
            user = await User.load(userid=user)
        if not isinstance(user, User):
            return
        
        self.reputation.rep_to(user.userid)
        user.reputation.rep_from(self.userid)

    async def cache_member_data(self, bot: commands.Bot, member: Optional[discord.Member] = None) -> None:
        if not member:
            guild = await retrieve_guild_strict(bot=bot, guild_id=CONFIG.GUILD_ID)
            member = await retrieve_member(guild=guild, member_id=int(self.userid))
            if not member:
                LOGGER.debug(f"Tried to cache member data of id {self.userid} in database but member was not found")
                return

        self.name = member.name
        self.display_name = member.display_name
        LOGGER.debug(f"Cached member data of id {self.userid} in database")

    def get_name(self) -> str:
        if self.name == "":
            return "UNKNOWN"
        return self.name
    
    def get_display_name(self) -> str:
        if self.display_name == "":
            return "UNKNOWN"
        return self.display_name
    
    async def get_tasks(self) -> list[str]:
        tasks = []
        if self.profile.is_empty():
            tasks.append("Set your profile with /profile change")
        if not self.sent_feedback:
            tasks.append("Submit feedback/ideas with /feedback")
        if self.economy.last_daily_stamp == 0:
            tasks.append("Collect your daily for the 1st time with /daily")
        if self.reputation.points_given == 0:
            tasks.append("Give someone a reputation point for the 1st time with /rep @user")

        all_relationships = await self.get_all_relationships()
        if len(all_relationships) == 0:
            tasks.append("Try starting a relationship with someone using /relationship greet @user")

        return tasks
    
    def get_daily_tasks(self) -> list[tuple[str, bool]]:
        tasks = [
            ("Do your daily with /daily", not self.economy.can_do_daily()),
            ("Give someone a reputation point with /rep @user", not self.reputation.can_do_rep())
        ]
        return tasks
    
    def add_accepted_command_cost(self, command_name: str) -> None:
        command_name = command_name.lower()
        if command_name not in self.accepted_command_cost:
            self.accepted_command_cost.append(command_name)
    
    def has_accepted_command_cost(self, command_name: str) -> bool:
        command_name = command_name.lower()
        return command_name in self.accepted_command_cost
    
    async def get_all_relationships(self) -> list[Relationship]:
        return await Relationship.findall_containing("user_ids", [self.userid])
    
    async def get_relationship_with_user(self, user_id: str) -> Optional[Relationship]:
        return await Relationship.find_containing("user_ids", [self.userid, user_id])
    
    # Will create a new relationship if both users have none yet
    async def load_relationship_with_user(self, user_id: str) -> Relationship:
        return await Relationship.load([self.userid, user_id])