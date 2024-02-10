from typing import Optional
from src.constants.config import Config
from src.entities.inventory_item import InventoryItem
from src.entities.user import User

CONFIG = Config.get_instance()
IMAGE_PATH = "src/assets/{category}/{name}.png"

class Item():
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
            requirements: list[str],
            needs_item: Optional[str] = None
        ) -> None:
        self.name = name
        self.unique = unique
        self.id = id
        self.display_name = display_name
        self.use = use
        self.color = color
        self.description = description
        self.category = category
        self.emoji_id = emoji_id
        self.price = price
        self.max_count = max_count
        self.data = data
        self.requirements = requirements
        self.needs_item = needs_item

    def has_requirements(self) -> bool:
        return len(self.requirements) > 0
    
    def get_requirements(self) -> str:
        return "\n".join(self.requirements)

    def get_inventory_item(self) -> InventoryItem:
        return InventoryItem(
            id=self.id,
            unique=self.unique,
            data=self.data.copy()
        )
    
    def get_emoji(self) -> str:
        return f"<:{self.name}:{self.emoji_id}>"
    
    def get_image_path(self) -> str:
        return IMAGE_PATH.format(category=self.category, name=self.name)
    
    def get_image_file_name(self) -> str:
        return f"{self.name}.png"
    
    def get_image_url(self) -> str:
        image_file_name = self.get_image_file_name()
        return f"attachment://{image_file_name}"

    def can_buy(self, user: User, amount: int) -> tuple[bool, str]:
        if self.needs_item:
            has_item = user.inventory.has_item(id=self.needs_item)
            if not has_item:
                return False, f"You dont meet all unlock requirements to buy this item.\nCheck the requirements with `/item {self.id}`."
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
        self.on_buy(user=user)
        await user.save()
        return True, ""
    
    def on_buy(self, user: User) -> None:
        return