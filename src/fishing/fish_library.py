from numpy import random
from typing import Optional
from src.constants.emoji_index import EmojiIndex
from src.fishing.fish_entry import FishEntry
from src.fishing.fish_rarity import FishRarity
from src.utils.file_operations import construct_path, file_to_dict, file_to_list
from src.utils.probability import WeightedSelector
from src.utils.progress_bar import progress_bar, get_progress_ratio

DATA_FILE_PATH = construct_path("src/data/fish.json")
BAIT_LEVELS_FILE_PATH = construct_path("src/data/bait_levels.json")

PRESTIGE_IMAGE_PATH = "src/assets/prestige/prestige_{level}.png"

EMOJI_INDEX = EmojiIndex.get_instance()

RARITY_LEVELS = 5
MAX_PRESTIGE = 5
PRESTIGE_LEVELS = {
    0: 0,
    1: 5,
    2: 15,
    3: 35,
    4: 75,
    5: 150
}
PRESTIGE_BONUS = {
    0: 0,
    1: 0.25,
    2: 0.75,
    3: 1.75,
    4: 3.75,
    5: 7.5
}
PRESTIGE_COLORS = {
    0: "#806052",
    1: "#e05b22",
    2: "#dbd7d5",
    3: "#f0c846",
    4: "#b041cc",
    5: "#29d8ff"
}

# How much prestige points fish of different rarity and prestige level give in total
PRESTIGE_POINTS = [
    [1, 2, 3, 4, 5],
    [3, 5, 7, 10, 12],
    [5, 8, 12, 16, 20],
    [10, 15, 20, 25, 30],
    [20, 30, 40, 50, 60]
]

class FishLibrary():
    _instance = None

    def __init__(self) -> None:
        if FishLibrary._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of FishLibrary.")
        self.fish_by_id = {}
        self.fish_by_name = {}
        self.fish_by_rarity = {i: [] for i in range(1, 6)}
        # Probabilities mapped to bait_levels[rod_level][bait_level]
        self.probabilities: list[list[WeightedSelector]] = []
        self._initialize_entries()
        self._initialize_bait_levels()
        self.fish_count = len(self.fish_by_id)

    def _initialize_entries(self) -> None:
        fish_data = file_to_dict(DATA_FILE_PATH)
        fish_list = []
        for id, data in fish_data.items():
            data["id"] = id
            entry = FishEntry.from_dict(data=data)
            fish_list.append(entry)
        
        sorted_fish_list = sorted(fish_list, key=lambda entry: (entry.rarity.value, entry.name))

        self.fish_by_id = {entry.id: entry for entry in sorted_fish_list}
        self.fish_by_name = {entry.name.lower(): entry for entry in sorted_fish_list}

        for entry in sorted_fish_list:
            self.fish_by_rarity[entry.rarity.value].append(entry)

    def _initialize_bait_levels(self) -> None:
        self.probabilities = []

        bait_levels_data = file_to_list(BAIT_LEVELS_FILE_PATH)
        
        for rarity_lvl in range(RARITY_LEVELS):
            rarity_probabilities = []
            
            for bait_data in bait_levels_data:
                weights = bait_data.get('weights', [])
                values = bait_data.get('values', [])
                # Adjust weights and values based on rarity level
                adjusted_weights = weights[:rarity_lvl + 1]
                adjusted_values = values[:rarity_lvl + 1]
                
                selector = WeightedSelector(weights=adjusted_weights, values=adjusted_values)
                rarity_probabilities.append(selector)
            
            self.probabilities.append(rarity_probabilities)

    @staticmethod
    def get_instance() -> 'FishLibrary':
        if FishLibrary._instance is None:
            FishLibrary._instance = FishLibrary()
        return FishLibrary._instance
    
    def find(self, identifier: str) -> Optional[FishEntry]:
        entry = self.get_by_name(identifier)
        if entry:
            return entry
        entry = self.get_by_id(identifier)
        if entry:
            return entry
        return None
    
    def get_by_id(self, id: str) -> Optional[FishEntry]:
        if id not in self.fish_by_id:
            return None
        return self.fish_by_id[id]
    
    def get_by_name(self, name: str) -> Optional[FishEntry]:
        name = name.lower()
        if name not in self.fish_by_name:
            return None
        return self.fish_by_name[name]

    def random_fish_entry(self, rod_level: int, bait_level: int) -> Optional[FishEntry]:
        probability = self.probabilities[rod_level][bait_level]
        rarity_level = probability.select()

        entries = self.fish_by_rarity[rarity_level]
        if len(entries) == 0:
            return None
        
        entry = random.choice(entries, size=1)[0]
        return entry
    
    # tuple[entry, caught?]
    def generate_fish_dex(self, caught_ids: list[str], rarity: Optional[str] = None) -> list[tuple[FishEntry, bool]]:
        if rarity:
            rarity_value = FishRarity.__members__.get(rarity.upper(), None)
        else:
            rarity_value = None
        
        entries = list(self.fish_by_id.values())

        dex = []
        for entry in entries:
            # Skip the entry if it doesnt equal the given rarity
            if isinstance(rarity_value, FishRarity) and entry.rarity != rarity_value:
                continue
            caught = False
            if entry.id in caught_ids:
                caught = True
            dex.append((entry, caught))
        return dex
    
    def calculate_cumulative_money(self, fishes: list[tuple[str, int]]) -> int:
        money = 0
        for fish_id, count in fishes:
            entry = self.get_by_id(fish_id)
            if not isinstance(entry, FishEntry):
                continue
            money += self.calculate_fish_price_cumulative(id=fish_id, count=count, fish_sold=count)
        return money
    
    def get_dex_stats(self, caught_ids: list[str]) -> str:
        count_by_rarity: dict[FishRarity, list[int]] = {rarity: [0, 0] for rarity in FishRarity}
        for entry in list(self.fish_by_id.values()):
            if entry.id in caught_ids:
                count_by_rarity[entry.rarity][0] += 1
                count_by_rarity[entry.rarity][1] += 1
            else:
                count_by_rarity[entry.rarity][1] += 1
            
        result = "\n".join([f"**`{found_vs_total[0]}/{found_vs_total[1]}`** **{rarity.name}**" for rarity, found_vs_total in count_by_rarity.items()])
        return result
    
    def get_prestige_level(self, fish_sold: int) -> int:
        for level, required in PRESTIGE_LEVELS.items():
            if fish_sold < required:
                return level - 1
        return MAX_PRESTIGE
    
    def get_prestige_level_and_percentage(self, fish_sold: int) -> tuple[int, float]:
        level = self.get_prestige_level(fish_sold=fish_sold)
        if self.prestige_is_maxed(level=level):
            return level, 1
        return level, get_progress_ratio(fish_sold, PRESTIGE_LEVELS[level], PRESTIGE_LEVELS[level + 1]) * 100

    def get_prestige_bonus(self, fish_sold: int) -> float:
        level = self.get_prestige_level(fish_sold=fish_sold)
        return PRESTIGE_BONUS[level]
    
    def get_prestige_emoji(self, level: int) -> str:
        level = max(0, min(level, MAX_PRESTIGE))
        return EMOJI_INDEX.get_emoji(f"prestige_{level}")
    
    def get_prestige_color(self, level: int) -> str:
        level = max(0, min(level, MAX_PRESTIGE))
        return PRESTIGE_COLORS[level]
    
    def prestige_is_maxed(self, level: int) -> bool:
        if level >= MAX_PRESTIGE:
            return True
        return False
    
    def get_prestige_image_path(self, level: int) -> str:
        return PRESTIGE_IMAGE_PATH.format(level=level)
    
    def get_prestige_image_file_name(self, level: int) -> str:
        return f"prestige_{level}.png"
    
    def get_prestige_image_url(self, level: int) -> str:
        image_file_name = self.get_prestige_image_file_name(level)
        return f"attachment://{image_file_name}"
    
    def fish_till_next_level(self, level: int, sold: int) -> int:
        if self.prestige_is_maxed(level=level):
            return 0
        return PRESTIGE_LEVELS[level + 1] - sold
    
    def get_prestige_progress(self, level: int, sold: int) -> str:
        if self.prestige_is_maxed(level=level):
            bar, percentage = progress_bar(0, 0, 0, 20)
        else:
            print(sold)
            print(level)
            bar, percentage = progress_bar(current=sold, start=PRESTIGE_LEVELS[level], end=PRESTIGE_LEVELS[level + 1], length=20)
        return bar + f" `({percentage*100}%)`"

    # Important for prestige levels, the higher the amount of sold fish, the better the price
    def calculate_fish_price_cumulative(self, id: str, count: int, fish_sold: int) -> int:
        fish_entry = self.get_by_id(id=id)
        if not isinstance(fish_entry, FishEntry):
            return 0
        price = fish_entry.price

        money = 0
        for _ in range(count):
            bonus = self.get_prestige_bonus(fish_sold=fish_sold)
            sell_price = price + bonus*price
            money += int(sell_price)
            fish_sold += 1
        return money
    
    def calculate_fish_price(self, id: str, fish_sold: int) -> int:
        fish_entry = self.get_by_id(id=id)
        if not isinstance(fish_entry, FishEntry):
            return 0
        price = fish_entry.price

        bonus = self.get_prestige_bonus(fish_sold=fish_sold)
        return int(price + bonus*price)
    
    def calculate_fish_price_from_prestige(self, id: str, prestige: int) -> int:
        fish_entry = self.get_by_id(id=id)
        if not isinstance(fish_entry, FishEntry):
            return 0
        price = fish_entry.price

        bonus = PRESTIGE_BONUS[prestige]
        return int(price + bonus*price)
    
    def get_prestige_points(self, fish_id: str, fish_sold: int) -> int:
        prestige_level = self.get_prestige_level(fish_sold=fish_sold)
        if prestige_level == 0:
            return 0
        
        fish_entry = self.get_by_id(id=fish_id)
        if not isinstance(fish_entry, FishEntry):
            return 0
        rarity = fish_entry.rarity.value
        
        try:
            return PRESTIGE_POINTS[rarity-1][prestige_level-1]
        except IndexError:
            raise RuntimeError(f"Cant calculate prestige points from rarity {rarity} and prestige level {prestige_level}, prestige points for this configuration werent defined yet.")
        
    def get_maximum_needed_fish_sold(self) -> int:
        return list(PRESTIGE_LEVELS.values())[-1]
    
    def get_fish_count(self) -> int:
        return self.fish_count