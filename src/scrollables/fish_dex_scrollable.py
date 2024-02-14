from src.constants.config import Config
from src.fishing.fish_library import FishEntry, FishLibrary
from src.scrollables.abstract_scrollable_query import AbstractScrollable

CONFIG = Config.get_instance()
FISH_LIBRARY = FishLibrary.get_instance()

PAGE_SIZE = 20

class FishDexScrollable(AbstractScrollable):
    def __init__(self, page_size: int, starting_page: int = 1) -> None:
        super().__init__(page_size, starting_page)

    # Takes in a list of tuples[entry, caught?, prestige_level, prestige_percentage]
    @staticmethod
    async def create(fish_dex: list[tuple[FishEntry, bool, int, float]]) -> 'FishDexScrollable':
        return await FishDexScrollable.create_from_entities(
            entities=fish_dex,
            page_size=PAGE_SIZE
        )
    
    async def output(self) -> str:
        fishes: list[tuple[FishEntry, bool, int, float]] = self.get_current_entities()
        if len(fishes) == 0:
            return "*no fish*"

        strings = []
        for fish_entry, caught, prestige, percentage in fishes:
            prestige_str = FISH_LIBRARY.get_prestige_emoji(level=prestige)
            if not isinstance(fish_entry, FishEntry):
                string = "ERROR"
            elif caught:
                string = f"**{fish_entry.rarity.name[0]}** {prestige_str} | {fish_entry.get_emoji()} **`{fish_entry.name}`** `{round(percentage, CONFIG.DECIMAL_DIGITS)}%`"
            else:
                string = f"**{fish_entry.rarity.name[0]}** {prestige_str} | **`?????`**"
            strings.append(string)
        return "\n".join(strings)