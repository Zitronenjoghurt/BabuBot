import random
from datetime import datetime, timedelta
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.utils.progress_bar import progress_bar

GROWTH_FACTOR = 1.1
LVL_1_MINUTES = 5
MIN_XP = 5
MAX_XP = 25
XP_COOLDOWN_MINS = 1
CURRENCY_PER_GAIN = 5

AVERAGE_XP = (MIN_XP+MAX_XP)/2

# How much XP is needed for each level
def level_to_xp(level: int) -> int:
    if level == 0:
        return 0
    result =  ((GROWTH_FACTOR**(level))/GROWTH_FACTOR)*LVL_1_MINUTES*AVERAGE_XP
    return int(result)

LEVEL_TOTAL_XP = {}
_cumulative_xp = 0
for level in range(0, 201):
    _cumulative_xp += level_to_xp(level)
    LEVEL_TOTAL_XP[level] = _cumulative_xp
del _cumulative_xp

LEVEL_REWARD = {}
for level in range(0, 201):
    required_xp = level_to_xp(level)
    number_gains = int(required_xp/AVERAGE_XP)
    LEVEL_REWARD[level] = int(number_gains*CURRENCY_PER_GAIN)

def total_xp_to_level(total_xp: int) -> int:
    for level, level_total_xp in LEVEL_TOTAL_XP.items():
        if total_xp < level_total_xp:
            return level - 1
    return -1

class Levels(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["total_xp", "next_gain", "redeemed_till_level"]

    def __init__(
            self,
            total_xp: Optional[int] = None,
            next_gain: Optional[float] = None,
            redeemed_till_level: Optional[int] = None
        ) -> None:
        if total_xp is None:
            total_xp = 0
        if next_gain is None:
            next_gain = 0
        if redeemed_till_level is None:
            redeemed_till_level = 0

        self.total_xp = total_xp
        self.next_gain = next_gain
        self.redeemed_till_level = redeemed_till_level

    def get_level(self) -> int:
        return total_xp_to_level(total_xp=self.total_xp)

    def can_gain(self) -> bool:
        now_stamp = datetime.now().timestamp()
        if now_stamp >= self.next_gain:
            return True
        return False

    # Returns true if the xp gain lead to a level up
    def gain(self) -> bool:
        if not self.can_gain():
            return False
        xp_gain = random.randint(MIN_XP, MAX_XP)
        next_gain = datetime.now() + timedelta(minutes=XP_COOLDOWN_MINS)
        
        level_before = self.get_level()
        self.total_xp += xp_gain
        self.next_gain = next_gain.timestamp()
        level_after = self.get_level()

        return level_after > level_before
    
    # Returns progress bar and percentage
    def get_level_progress(self) -> tuple[str, float]:
        lvl = self.get_level()
        current_lvl_xp = LEVEL_TOTAL_XP[lvl]
        next_lvl_xp = LEVEL_TOTAL_XP[lvl+1]

        return progress_bar(self.total_xp, current_lvl_xp, next_lvl_xp, 20)
    
    def get_xp_progress(self) -> tuple[int, int]:
        lvl = self.get_level()
        current_gained = self.total_xp - LEVEL_TOTAL_XP[lvl]
        current_needed = LEVEL_TOTAL_XP[lvl+1] - LEVEL_TOTAL_XP[lvl]
        return current_gained, current_needed
    
    def has_pending_reward(self) -> bool:
        return self.get_level() > self.redeemed_till_level
    
    # Returns the reward and if it was the first time some reward was collected
    def collect_reward(self) -> tuple[int, bool]:
        if not self.has_pending_reward():
            return 0, False
        
        first_time = False
        if self.redeemed_till_level == 0:
            first_time = True

        level = self.get_level()

        reward = 0
        for lvl in range(self.redeemed_till_level, level+1):
            reward += LEVEL_REWARD[lvl]
        
        self.redeemed_till_level = level
        return reward, first_time