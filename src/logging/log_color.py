import discord
from enum import Enum

class LogColor(Enum):
    DM = discord.Color.from_str("#68E397")
    INFO = discord.Color.from_str("#3474EB")
    ERROR = discord.Color.red()
    SUCCESS = discord.Color.green()
    WARNING = discord.Color.yellow()