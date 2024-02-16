from src.items.item import Item
from src.scrollables.abstract_scrollable_query import AbstractScrollable

PAGE_SIZE = 25

class InventoryScrollable(AbstractScrollable):
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        super().__init__(page_size, starting_page)

    @staticmethod
    async def create(items_with_count: list[tuple[Item, int]]) -> 'InventoryScrollable':
        return await InventoryScrollable.create_from_entities(
            entities=items_with_count,
            page_size=PAGE_SIZE
        )
    
    async def output(self) -> str:
        items: list[tuple[Item, int]] = self.get_current_entities()
        if len(items) == 0:
            return "*no items*"

        strings = []
        for item, count in items:
            string = f"**`{item.id}`** ❥ {item.get_emoji()} **{item.display_name}** | `{count}x`"
            strings.append(string)
        return "\n".join(strings)