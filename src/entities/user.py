import discord
from discord.ext import commands
from typing import Optional
from src.entities.abstract_entity import AbstractEntity

class User(AbstractEntity):
    TABLE_NAME = "users"
    SAVED_PROPERTIES = ["id", "userid", "message_count"]

    def __init__(self, id: Optional[int] = None, userid: Optional[str] = None, message_count: Optional[int] = None) -> None:
        super().__init__(id=id)
        if userid is None:
            userid = ""
        if message_count is None:
            message_count = 0

        self.userid = str(userid)
        self.message_count = int(message_count)
    
    def count_message(self) -> None:
        self.message_count += 1

    async def fetch_discord_user(self, bot: commands.Bot) -> Optional[discord.User]:
        user = await bot.fetch_user(self.userid)
        return user