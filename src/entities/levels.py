import math
from datetime import datetime, timedelta
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

GROWTH_FACTOR = 1.1
LVL_1_MINUTES = 5
MIN_XP = 5
MAX_XP = 25
XP_COOLDOWN_MINS = 1

AVERAGE_XP = (MIN_XP+MAX_XP)/2

# How much XP is needed for each level
def level_to_xp(level: int) -> int:
    result =  ((GROWTH_FACTOR**(level))/GROWTH_FACTOR)*LVL_1_MINUTES*AVERAGE_XP
    return int(result)

LEVEL_TOTAL_XP = {}
_cumulative_xp = 0
for level in range(1, 201):
    _cumulative_xp += level_to_xp(level)
    LEVEL_TOTAL_XP[level] = _cumulative_xp
del _cumulative_xp

def total_xp_to_level(total_xp: int) -> int:
    for level, level_total_xp in LEVEL_TOTAL_XP.items():
        if total_xp <= level_total_xp:
            return level
    return -1

class Levels(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["total_xp", "next_gain"]

    def __init__(
            self,
            total_xp: Optional[int] = None,
            next_gain: Optional[float] = None
        ) -> None:
        if total_xp is None:
            total_xp = 0
        if next_gain is None:
            next_gain = 0

        self.total_xp = total_xp
        self.next_gain = next_gain