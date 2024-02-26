import discord
from datetime import datetime
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.digging import Digging
from src.entities.economy import Economy
from src.entities.inventory import Inventory
from src.entities.fishing import Fishing
from src.entities.levels import Levels
from src.entities.message_statistics import MessageStatistics
from src.entities.profile import Profile
from src.entities.relationship import Relationship
from src.entities.reputation import Reputation
from src.entities.word_counter_toplist import WordCounterToplist
from src.entities.word_counter import WordCounter
from src.logging.logger import LOGGER
from src.utils.bot_operations import retrieve_guild_strict
from src.utils.dict_operations import sort_simple
from src.utils.discord_time import relative_time
from src.utils.guild_operations import retrieve_member
from src.utils.validator import validate_of_type

CONFIG = Config.get_instance()

class DiggingQueueItem(AbstractDatabaseEntity):
    TABLE_NAME = "digging_queue"
    SERIALIZED_PROPERTIES = ["id", "created_stamp"]
    SAVED_PROPERTIES = ["userid", "created_stamp"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)