import discord
from typing import Optional
from src.scrollables.abstract_scrollable import AbstractScrollable

class ScrollableEmbed(discord.Embed):
    def __init__(
            self,
            scrollable,
            title: Optional[str] = None,
            color: Optional[discord.Colour] = None,
            author: Optional[str] = None,
            icon_url: Optional[str] = None
        ) -> None:
        if not isinstance(scrollable, AbstractScrollable):
            raise RuntimeError(f"Tried to initialize scrollable embed but given scrollable is invalid.")
        super().__init__(title=title, color=color)
        
        self.scrollable = scrollable
        if author:
            self.set_author(name=author, icon_url=icon_url)

    def is_scrollable(self) -> bool:
        return self.scrollable.is_scrollable()
    
    def time_out(self) -> None:
        self.color = discord.Color.dark_grey()
        self.set_footer(text="This interaction has timed out.")

    async def initialize(self) -> None:
        self.description = await self.scrollable.output()
        self.set_footer(text=self.scrollable.get_footer())

    async def next(self) -> None:
        self.description = await self.scrollable.next()
        self.set_footer(text=self.scrollable.get_footer())

    async def previous(self) -> None:
        self.description = await self.scrollable.previous()
        self.set_footer(text=self.scrollable.get_footer())