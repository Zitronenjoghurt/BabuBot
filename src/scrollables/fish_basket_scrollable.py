from src.constants.config import Config
from src.fishing.fish_library import FishEntry, FishLibrary
from src.scrollables.abstract_scrollable_query import AbstractScrollable

CONFIG = Config.get_instance()
FISH_LIBRARY = FishLibrary.get_instance()

PAGE_SIZE = 25

class FishBasketScrollable(AbstractScrollable):
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        super().__init__(page_size, starting_page)

    # Takes in a list of tuples[fish_id, count, prestige]
    @staticmethod
    async def create(fishes: list[tuple[str, int, int]]) -> 'FishBasketScrollable':
        fish_entries_with_count = []
        for fish_id, count, prestige in fishes:
            fish_entry = FISH_LIBRARY.get_by_id(fish_id)
            if fish_entry:
                fish_entries_with_count.append((fish_entry, count, prestige))
        
        fish_entries_with_count.sort(key=lambda x: (-x[0].rarity.value, x[0].name))

        entities = [(entry[0], entry[1], entry[2]) for entry in fish_entries_with_count]

        return await FishBasketScrollable.create_from_entities(
            entities=entities,
            page_size=PAGE_SIZE
        )
    
    async def output(self) -> str:
        fishes: list[tuple[FishEntry, int, int]] = self.get_current_entities()
        if len(fishes) == 0:
            return "*no fish*"

        strings = []
        for fish_entry, count, prestige in fishes:
            if fish_entry is None:
                string = "ERROR"
            else:
                price = FISH_LIBRARY.calculate_fish_price_from_prestige(fish_entry.id, prestige)
                string = f"❥ `{count}x` {fish_entry.get_emoji()} **`{fish_entry.name}`** | **{fish_entry.rarity.name[0]}** **`{price}{CONFIG.CURRENCY}`**"
            strings.append(string)
        return "\n".join(strings)