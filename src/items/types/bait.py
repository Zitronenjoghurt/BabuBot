from src.items.item import Item

class Bait(Item):
    def __init__(self, name: str, unique: bool, id: str, display_name: str, color: str, description: str, use: str, category: str, emoji_id: str, price: int, max_count: int, data: dict) -> None:
        super().__init__(name, unique, id, display_name, color, description, use, category, emoji_id, price, max_count, data)