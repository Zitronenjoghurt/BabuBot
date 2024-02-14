from datetime import datetime
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.fishing.fish_entry import FishEntry
from src.fishing.fish_library import FishLibrary, PRESTIGE_LEVELS

FISHING_COOLDOWN = 300
FISH_LIBRARY = FishLibrary.get_instance()

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
    
    def get_fishes_with_count_and_prestige(self) -> list[tuple[str, int, int]]:
        fishes = []
        for fish_id, data in self.caught_fish.items():
            count = data.get("count", 0)
            if count > 0:
                fishes.append((fish_id, count, self.get_prestige_level(fish_id=fish_id)))
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
    
    def get_cumulative_money(self) -> int:
        fishes = self.get_fishes_with_total_count_difference()
        return FISH_LIBRARY.calculate_cumulative_money(fishes=fishes)
    
    # tuple[entry, caught?, prestige_level, prestige_percentage]
    def get_fish_dex(self, rarity: Optional[str] = None) -> list[tuple[FishEntry, bool, int, float]]:
        caught_ids = self.get_fishes()

        fish_dex = FISH_LIBRARY.generate_fish_dex(caught_ids=caught_ids, rarity=rarity)
        fish_dex_with_prestige = []
        for entry, caught in fish_dex:
            if not caught:
                fish_dex_with_prestige.append((entry, caught, 0, 0))
            else:
                fish_sold = self.get_fish_sold(fish_id=entry.id)
                level, percentage = FISH_LIBRARY.get_prestige_level_and_percentage(fish_sold=fish_sold)
                fish_dex_with_prestige.append((entry, caught, level, percentage))
        return fish_dex_with_prestige
    
    def get_fish_dex_stats(self) -> str:
        caught_ids = self.get_fishes()
        return FISH_LIBRARY.get_dex_stats(caught_ids=caught_ids)
    
    def get_fish_sold(self, fish_id: str) -> int:
        if fish_id not in self.caught_fish:
            return 0
        fish_data = self.caught_fish[fish_id]
        total = fish_data.get("total_count", 0)
        current = fish_data.get("count", 0)

        return max(total-current, 0)

    def get_fish_sell_amount_and_money(self) -> tuple[int, int]:
        fishes_to_sell = self.get_fishes_to_sell()

        money = 0
        total_count = 0
        for fish_id, count in fishes_to_sell:
            fish_sold = self.get_fish_sold(fish_id=fish_id)
            money += FISH_LIBRARY.calculate_fish_price_cumulative(id=fish_id, count=count, fish_sold=fish_sold)
            total_count += count

        return total_count, money 
    
    def get_prestige_level(self, fish_id: str) -> int:
        sold = self.get_fish_sold(fish_id=fish_id)
        return FISH_LIBRARY.get_prestige_level(fish_sold=sold)
    
    def get_prestige_progress(self, fish_id: str) -> str:
        sold = self.get_fish_sold(fish_id=fish_id)
        prestige_level = FISH_LIBRARY.get_prestige_level(fish_sold=sold)
        is_maxed = FISH_LIBRARY.prestige_is_maxed(level=prestige_level)

        if is_maxed:
            return "**MAXED**"
        else:
            next_sold = PRESTIGE_LEVELS[prestige_level+1]
            bar = f"{FISH_LIBRARY.get_prestige_emoji(level=prestige_level+1)} "+FISH_LIBRARY.get_prestige_progress(level=prestige_level, sold=sold)
            return f"{bar}\nSold: **{sold} out of {next_sold}**"
        
    def get_prestige_stats(self) -> str:
        prestige_stats = {lvl: 0 for lvl in range(0, 6)}
        for fish_id in self.caught_fish.keys():
            level = self.get_prestige_level(fish_id=fish_id)
            prestige_stats[level] += 1
        return "\n".join(f"**`{count}x {lvl}★`**" for lvl, count in prestige_stats.items())