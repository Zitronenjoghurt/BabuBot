from typing import Optional
from src.entities.user import User
from src.items.item import Item
from src.logging.logger import LOGGER

class FishingRod(Item):
    def __init__(
            self, 
            name: str, 
            unique: bool, 
            id: str, 
            display_name: str,
            color: str, 
            description: str, 
            use: str, 
            category: str, 
            emoji_id: str, 
            price: int, 
            max_count: int, 
            data: dict,
            fish_count_till_available: int,
            rod_level: int,
            requirements: list[str],
            buy_message: Optional[str] = None,
            needs_item: Optional[str] = None
        ) -> None:
        super().__init__(
            name=name, 
            unique=unique, 
            id=id, 
            display_name=display_name, 
            color=color, 
            description=description, 
            use=use, 
            category=category, 
            emoji_id=emoji_id, 
            price=price, 
            max_count=max_count, 
            data=data,
            requirements=requirements,
            buy_message=buy_message,
            needs_item=needs_item)
        self.fish_count_till_unlock = fish_count_till_available
        self.rod_level = rod_level

    def can_buy(self, user: User, amount: int) -> tuple[bool, str]:
        status, message =  super().can_buy(user, amount)
        if not status:
            return False, message
        total_fish_count = user.fishing.get_total_fish_count()
        if total_fish_count < self.fish_count_till_unlock:
            difference = self.fish_count_till_unlock - total_fish_count
            return False, f"You need to catch `{difference}` more fish before you can buy this rod."
        return True, ""
    
    def on_buy(self, user: User) -> None:
        if not user.fishing.unlocked:
            user.fishing.unlock()
            LOGGER.debug(f"FISH: User {user.get_name()} ({user.userid}) has unlocked the fishing game")
        if self.rod_level > user.fishing.rod_level:
            LOGGER.debug(f"FISH: User {user.get_name()} ({user.userid}) has gained a new rod level: {self.rod_level}")
            user.fishing.rod_level = self.rod_level