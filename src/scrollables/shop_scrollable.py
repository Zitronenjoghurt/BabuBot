from src.constants.config import Config
from src.items.item import Item
from src.scrollables.abstract_scrollable_query import AbstractScrollable

CONFIG = Config.get_instance()
PAGE_SIZE = 20

class ShopScrollable(AbstractScrollable):
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        super().__init__(page_size, starting_page)

    @staticmethod
    async def create(items: list[Item]) -> 'ShopScrollable':
        return await ShopScrollable.create_from_entities(
            entities=items,
            page_size=PAGE_SIZE
        )
    
    async def output(self) -> str:
        items: list[Item] = self.get_current_entities()
        if len(items) == 0:
            return "*no items*"

        strings = []
        for item in items:
            string = f"**`{item.id}`** ❥ <:{item.name}:{item.emoji_id}> **{item.display_name}** | `({item.price}{CONFIG.CURRENCY})`"
            strings.append(string)
        return "\n".join(strings)