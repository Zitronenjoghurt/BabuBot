from src.items.item import Item

class FishingRod(Item):
    def __init__(self, name: str, unique: bool, id: str, display_name: str, description: str, category: str, emoji_id: str, price: int, max_count: int, data: dict, fish_count_till_available: int) -> None:
        super().__init__(name, unique, id, display_name, description, category, emoji_id, price, max_count, data)
        self.fish_count_till_unlock = fish_count_till_available