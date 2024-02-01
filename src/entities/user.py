import discord
from discord.ext import commands
from typing import Optional
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.word_counter import WordCounter
from src.utils.validator import validate_of_type

class User(AbstractDatabaseEntity):
    TABLE_NAME = "users"
    SERIALIZED_PROPERTIES = ["id", "userid", "word_counter"]
    SERIALIZE_CLASSES = {"word_counter": WordCounter}

    def __init__(
            self, 
            id: Optional[int] = None, 
            userid: Optional[str] = None, 
            word_counter: Optional[WordCounter] = None
        ) -> None:
        super().__init__(id=id)
        if userid is None:
            userid = ""
        if word_counter is None:
            word_counter = WordCounter()

        validate_of_type(word_counter, WordCounter, "word_counter")

        self.userid = str(userid)
        self.word_counter: WordCounter = word_counter

    async def fetch_discord_user(self, bot: commands.Bot) -> Optional[discord.User]:
        user = await bot.fetch_user(self.userid)
        return user