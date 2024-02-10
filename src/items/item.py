from src.constants.config import Config
from src.entities.inventory_item import InventoryItem
from src.entities.user import User

CONFIG = Config.get_instance()

class Item():
    def __init__(
            self,
            name: str,
            unique: bool,
            id: str,
            display_name: str,
            description: str,
            category: str,
            emoji_id: str,
            price: int,
            max_count: int,
            data: dict
        ) -> None:
        self.name = name
        self.unique = unique
        self.id = id
        self.display_name = display_name
        self.description = description
        self.category = category
        self.emoji_id = emoji_id
        self.price = price
        self.max_count = max_count
        self.data = data

    def get_inventory_item(self) -> InventoryItem:
        return InventoryItem(
            id=self.id,
            unique=self.unique,
            data=self.data.copy()
        )
    
    def get_emoji(self) -> str:
        return f"<:{self.name}:{self.emoji_id}>"
    
    def can_buy(self, user: User, amount: int) -> tuple[bool, str]:
        item_count = user.inventory.item_count(self.id)
        if item_count + amount > self.max_count:
            return False, f"You can only own this item `{self.max_count}x`"
        if user.economy.currency < self.price * amount:
            return False, f"You need at least **`{self.price * amount}{CONFIG.CURRENCY}`** to buy this."
        return True, ""
    
    async def buy(self, user: User, amount: int = 1) -> tuple[bool, str]:
        status, message = self.can_buy(user=user, amount=amount)
        if not status:
            return False, message
        success = user.economy.remove_currency(self.price * amount)
        if not success:
            return False, f"You need at least **`{self.price}{CONFIG.CURRENCY}`** to buy this item."
        inventory_item = self.get_inventory_item()
        user.inventory.add_item(inventory_item, count=amount)
        await user.save()
        return True, ""