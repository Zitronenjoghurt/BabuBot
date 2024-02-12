from datetime import datetime
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.fishing.fish_entry import FishEntry

FISHING_COOLDOWN = 300

class Fishing(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["unlocked", "started_at", "rod_level", "caught_fish", "next_fishing_stamp", "leave_one"]

    def __init__(
            self,
            unlocked: Optional[bool] = None,
            started_at: Optional[float] = None,
            rod_level: Optional[int] = None,
            caught_fish: Optional[dict] = None,
            next_fishing_stamp: Optional[float] = None,
            leave_one: Optional[bool] = None
        ) -> None:
        if unlocked is None:
            unlocked = False
        if started_at is None:
            started_at = 0
        if rod_level is None:
            rod_level = 0
        if caught_fish is None:
            caught_fish = {}
        if next_fishing_stamp is None:
            next_fishing_stamp = 0
        if leave_one is None:
            leave_one = False
        
        self.unlocked = unlocked
        self.started_at = started_at
        self.rod_level = rod_level
        self.caught_fish = caught_fish
        self.next_fishing_stamp = next_fishing_stamp
        self.leave_one = leave_one

    def unlock(self) -> None:
        if not self.unlocked:
            self.unlocked = True
            self.started_at = datetime.now().timestamp()

    def has_caught(self, fish_id) -> bool:
        if fish_id in self.caught_fish:
            return True
        return False
    
    def can_fish(self) -> bool:
        if datetime.now().timestamp() > self.next_fishing_stamp:
            return True
        return False

    # returns first_catch, record_size
    def process_fish(self, fish_entry: FishEntry, size: float) -> tuple[bool, bool]:
        id = fish_entry.id

        self.next_fishing_stamp = datetime.now().timestamp() + FISHING_COOLDOWN

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
    
    def get_fishes(self) -> list[str]:
        fishes = []
        for fish_id in self.caught_fish.keys():
            fishes.append(fish_id)
        return fishes
    
    def get_fishes_to_sell(self) -> list[tuple[str, int]]:
        fishes = []
        for fish_id, data in self.caught_fish.items():
            count = data.get("count", 0)
            if not self.leave_one:
                if count > 0:
                    fishes.append((fish_id, count))
            else:
                if count > 1:
                    fishes.append((fish_id, count - 1))
        return fishes
    
    def get_fishes_with_count(self) -> list[tuple[str, int]]:
        fishes = []
        for fish_id, data in self.caught_fish.items():
            count = data.get("count", 0)
            if count > 0:
                fishes.append((fish_id, count))
        return fishes
    
    def get_fishes_with_total_count(self) -> list[tuple[str, int]]:
        fishes = []
        for fish_id, data in self.caught_fish.items():
            count = data.get("total_count", 0)
            if count > 0:
                fishes.append((fish_id, count))
        return fishes
    
    def get_fishes_with_total_count_difference(self) -> list[tuple[str, int]]:
        fishes = []
        for fish_id, data in self.caught_fish.items():
            total_count = data.get("total_count", 0)
            count = data.get("count", 0)
            difference = total_count - count
            if difference > 0:
                fishes.append((fish_id, difference))
        return fishes
    
    def sell_all(self) -> None:
        for fish_id, data in self.caught_fish.items():
            count = data.get("count", 0)
            if not self.leave_one:
                if count > 0:
                    self.caught_fish[fish_id]["count"] = 0
            else:
                if count > 1:
                    self.caught_fish[fish_id]["count"] = 1

    def get_total_fish_count(self) -> int:
        total_count = 0
        for entry in self.caught_fish.values():
            count = entry.get("total_count", 0)
            total_count += count
        return total_count
    
    def get_basket_fish_count(self) -> int:
        total_count = 0
        for entry in self.caught_fish.values():
            count = entry.get("count", 0)
            total_count += count
        return total_count