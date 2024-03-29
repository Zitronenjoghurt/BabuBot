import asyncio
import discord
from datetime import datetime
from typing import Optional
from src.constants.config import Config
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.digging import Digging
from src.entities.digging_queue import DiggingQueueItem
from src.entities.economy import Economy
from src.entities.inventory import Inventory
from src.entities.fishing import Fishing
from src.entities.levels import Levels
from src.entities.message_statistics import MessageStatistics
from src.entities.profile import Profile
from src.entities.relationship import Relationship
from src.entities.reputation import Reputation
from src.entities.settings import Settings
from src.entities.word_counter_toplist import WordCounterToplist
from src.entities.word_counter import WordCounter
from src.utils.dict_operations import sort_simple
from src.utils.discord_time import relative_time
from src.utils.validator import validate_of_type

CONFIG = Config.get_instance()

class User(AbstractDatabaseEntity):
    TABLE_NAME = "users"
    SERIALIZED_PROPERTIES = ["id", "userid", "created_stamp", "name", "display_name", "sent_feedback", "accepted_command_cost", "message_statistics", "word_counter", "profile", "economy", "reputation", "inventory", "fishing", "levels", "digging", "settings"]
    SERIALIZE_CLASSES = {"word_counter": WordCounter, "message_statistics": MessageStatistics, "profile": Profile, "economy": Economy, "reputation": Reputation, "inventory": Inventory, "fishing": Fishing, "levels": Levels, "digging": Digging, "settings": Settings}
    SAVED_PROPERTIES = ["userid", "created_stamp", "name", "display_name", "sent_feedback", "accepted_command_cost", "message_statistics", "word_counter", "profile", "economy", "reputation", "inventory", "fishing", "levels", "digging", "settings"]

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
            reputation: Optional[Reputation] = None,
            inventory: Optional[Inventory] = None,
            fishing: Optional[Fishing] = None,
            levels: Optional[Levels] = None,
            digging: Optional[Digging] = None,
            settings: Optional[Settings] = None
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
        if inventory is None:
            inventory = Inventory()
        if fishing is None:
            fishing = Fishing()
        if levels is None:
            levels = Levels()
        if digging is None:
            digging = Digging()
        if settings is None:
            settings = Settings()

        validate_of_type(message_statistics, MessageStatistics, "message_statistics")
        validate_of_type(word_counter, WordCounter, "word_counter")
        validate_of_type(profile, Profile, "profile")
        validate_of_type(economy, Economy, "economy")
        validate_of_type(reputation, Reputation, "reputation")
        validate_of_type(inventory, Inventory, "inventory")
        validate_of_type(fishing, Fishing, "fishing")
        validate_of_type(levels, Levels, "levels")
        validate_of_type(digging, Digging, "digging")
        validate_of_type(settings, Settings, "settings")

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
        self.inventory: Inventory = inventory
        self.fishing: Fishing = fishing
        self.levels: Levels = levels
        self.digging: Digging = digging
        self.settings: Settings = settings
        
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
    
    @staticmethod
    async def global_prestige_point_toplist() -> list['User']:
        users: list[User] = [user for user in await User.findall() if user.fishing.unlocked]
        users.sort(key=lambda user: user.fishing.get_current_prestige_points(), reverse=True)
        return users
    
    @staticmethod
    async def global_fishing_money_earned_toplist() -> list['User']:
        users: list[User] = [user for user in await User.findall() if user.fishing.unlocked]
        users.sort(key=lambda user: user.fishing.get_cumulative_money(), reverse=True)
        return users
    
    @staticmethod
    async def global_fish_sold_toplist() -> list['User']:
        users: list[User] = [user for user in await User.findall() if user.fishing.unlocked]
        users.sort(key=lambda user: user.fishing.get_total_fish_sold(), reverse=True)
        return users
    
    def get_created_time(self) -> datetime:
        return datetime.fromtimestamp(self.created_stamp)
    
    async def rep_user(self, user: 'User|str') -> None:
        if isinstance(user, str):
            user = await User.load(userid=user)
        if not isinstance(user, User):
            return
        
        self.reputation.rep_to(user.userid)
        user.reputation.rep_from(self.userid)

    def get_name(self) -> str:
        if self.name == "":
            return f"<{self.userid}>"
        return self.name
    
    def get_display_name(self) -> str:
        if self.display_name == "":
            return f"<{self.userid}>"
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
        if not self.fishing.unlocked:
            tasks.append("Buy a fishing rod with /buy R1 and get fishing with /fish")
        if self.fishing.get_basket_fish_count() > 0:
            tasks.append("You currently have fish in your basket, sell them with /fish-sell to gain money")

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
    
    def get_cooldowns(self) -> str:
        return f"**FISHING:** {relative_time(int(self.fishing.next_fishing_stamp))}"
    
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
    
    async def get_digging_queue(self) -> list[DiggingQueueItem]:
        return await DiggingQueueItem.get_user_queue_items(user_id=self.userid)
    
    async def queue_digging_item(self, item_id: str, seconds: int) -> tuple[bool, str]:
        digging_queue = await self.get_digging_queue()

        if not self.digging.queue_slot_available(digging_queue=digging_queue):
            return False, "There is currently no dwarf squad available."
        
        now = datetime.now().timestamp()
        finish_stamp = now + seconds
        queue_item = DiggingQueueItem(user_id=self.userid, item_id=item_id, finish_stamp=finish_stamp)
        await queue_item.save()
        return True, ""