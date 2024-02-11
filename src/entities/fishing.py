from datetime import datetime
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.fishing.fish_entry import FishEntry

class Fishing(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["unlocked", "started_at", "total_fish_count", "rod_level", "caught_fish"]

    def __init__(
            self,
            unlocked: Optional[bool] = None,
            started_at: Optional[float] = None,
            total_fish_count: Optional[int] = None,
            rod_level: Optional[int] = None,
            caught_fish: Optional[dict] = None
        ) -> None:
        if unlocked is None:
            unlocked = False
        if started_at is None:
            started_at = 0
        if total_fish_count is None:
            total_fish_count = 0
        if rod_level is None:
            rod_level = 0
        if caught_fish is None:
            caught_fish = {}
        
        self.unlocked = unlocked
        self.started_at = started_at
        self.total_fish_count = total_fish_count
        self.rod_level = rod_level
        self.caught_fish = caught_fish

    def unlock(self) -> None:
        if not self.unlocked:
            self.unlocked = True
            self.started_at = datetime.now().timestamp()

    def process_fish(self, fish_entry: FishEntry) -> None:
        size = fish_entry.get_random_size()
        id = fish_entry.id

        if id not in self.caught_fish:
            self.caught_fish[id] = {
                "total_count": 1,
                "count": 1,
                "min_size": size,
                "max_size": size
            }
            return
        self.caught_fish[id]["total_count"] += 1
        self.caught_fish[id]["count"] += 1

        if size < self.caught_fish[id]["min_size"]:
            self.caught_fish[id]["min_size"] = size
        elif size > self.caught_fish[id]["max_size"]:
            self.caught_fish[id]["max_size"] = size