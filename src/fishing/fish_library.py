from numpy import random
from typing import Optional
from src.fishing.fish_entry import FishEntry
from src.utils.file_operations import construct_path, file_to_dict, file_to_list
from src.utils.probability import WeightedSelector

DATA_FILE_PATH = construct_path("src/data/fish.json")
BAIT_LEVELS_FILE_PATH = construct_path("src/data/bait_levels.json")

RARITY_LEVELS = 5

class FishLibrary():
    _instance = None

    def __init__(self) -> None:
        if FishLibrary._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of FishLibrary.")
        self.fish = {}
        self.fish_by_rarity = {i: [] for i in range(1, 6)}
        # Probabilities mapped to bait_levels[rod_level][bait_level]
        self.probabilities: list[list[WeightedSelector]] = []
        self._initialize_entries()
        self._initialize_bait_levels()

    def _initialize_entries(self) -> None:
        fish_data = file_to_dict(DATA_FILE_PATH)
        for id, data in fish_data.items():
            data["id"] = id
            entry = FishEntry.from_dict(data=data)
            self.fish[id] = entry
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
    
    def get_by_id(self, id: str) -> Optional[FishEntry]:
        if id not in self.fish:
            return None
        return self.fish[id]
    
    def random_fish_entry(self, rod_level: int, bait_level: int) -> Optional[FishEntry]:
        probability = self.probabilities[rod_level][bait_level]
        rarity_level = probability.select()

        entries = self.fish_by_rarity[rarity_level]
        if len(entries) == 0:
            return None
        
        entry = random.choice(entries, size=1)[0]
        return entry