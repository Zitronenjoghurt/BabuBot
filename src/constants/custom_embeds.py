import discord

class SuccessEmbed(discord.Embed):
    def __init__(self, title: str, message: str) -> None:
        super().__init__(title=title, description=message, color=discord.Color.from_str("#48c744"))

class ErrorEmbed(discord.Embed):
    def __init__(self, title: str, message: str) -> None:
        super().__init__(title=title, description=message, color=discord.Color.from_str("#c9042f"))