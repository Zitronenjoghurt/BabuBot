from src.constants.config import Config
from src.fishing.fish_library import FishEntry, FishLibrary
from src.scrollables.abstract_scrollable_query import AbstractScrollable

CONFIG = Config.get_instance()
FISH_LIBRARY = FishLibrary.get_instance()

PAGE_SIZE = 30

class FishBasketScrollable(AbstractScrollable):
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        super().__init__(page_size, starting_page)

    # Takes in a list of tuples[fish_id, count]
    @staticmethod
    async def create(fishes: list[tuple[str, int]]) -> 'FishBasketScrollable':
        fish_entries_with_count = []
        for fish_id, count in fishes:
            fish_entry = FISH_LIBRARY.get_by_id(fish_id)
            if fish_entry:
                fish_entries_with_count.append((fish_entry, count))
        
        fish_entries_with_count.sort(key=lambda x: (-x[0].rarity.value, -x[0].price, x[0].name))

        entities = [(entry[0], entry[1]) for entry in fish_entries_with_count]

        return await FishBasketScrollable.create_from_entities(
            entities=entities,
            page_size=PAGE_SIZE
        )
    
    async def output(self) -> str:
        fishes: list[tuple[FishEntry, int]] = self.get_current_entities()
        if len(fishes) == 0:
            return "*no fish*"

        strings = []
        for fish_entry, count in fishes:
            if fish_entry is None:
                string = "ERROR"
            else:
                string = f"❥ `{count}x` {fish_entry.get_emoji()} **`{fish_entry.name}`** | **{fish_entry.rarity.name[0]}** **`{fish_entry.price}{CONFIG.CURRENCY}`**"
            strings.append(string)
        return "\n".join(strings)