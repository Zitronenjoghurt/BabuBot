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

    def has_caught(self, fish_id) -> bool:
        if fish_id in self.caught_fish:
            return True
        return False

    # returns first_catch, record_size
    def process_fish(self, fish_entry: FishEntry, size: float) -> tuple[bool, bool]:
        id = fish_entry.id

        self.total_fish_count += 1
        if id not in self.caught_fish:
            self.caught_fish[id] = {
                "total_count": 1,
                "count": 1,
                "min_size": size,
                "max_size": size,
                "first_catch_stamp": datetime.now().timestamp(),
                "last_catch_stamp": datetime.now().timestamp()
            }
            return True, False
        self.caught_fish[id]["total_count"] += 1
        self.caught_fish[id]["count"] += 1
        self.caught_fish[id]["last_catch_stamp"] = datetime.now().timestamp()

        if size < self.caught_fish[id]["min_size"]:
            self.caught_fish[id]["min_size"] = size
            return False, False
        elif size > self.caught_fish[id]["max_size"]:
            self.caught_fish[id]["max_size"] = size
            return False, True
        return False, False
    
    def get_total_count(self, fish_id: str) -> int:
        if not self.caught_fish[fish_id]:
            return 0
        return self.caught_fish[fish_id].get("total_count", 0)
    
    def get_current_count(self, fish_id: str) -> int:
        if not self.caught_fish[fish_id]:
            return 0
        return self.caught_fish[fish_id].get("count", 0)
    
    def get_min_size(self, fish_id: str) -> float:
        if not self.caught_fish[fish_id]:
            return 0
        return self.caught_fish[fish_id].get("min_size", 0)
    
    def get_max_size(self, fish_id: str) -> float:
        if not self.caught_fish[fish_id]:
            return 0
        return self.caught_fish[fish_id].get("max_size", 0)
    
    def get_first_catch_stamp(self, fish_id: str) -> float:
        if not self.caught_fish[fish_id]:
            return 0
        return self.caught_fish[fish_id].get("first_catch_stamp", 0)
    
    def get_last_catch_stamp(self, fish_id: str) -> float:
        if not self.caught_fish[fish_id]:
            return 0
        return self.caught_fish[fish_id].get("last_catch_stamp", 0)