from datetime import datetime
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class Fishing(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["unlocked", "started_at", "total_fish_count"]

    def __init__(
            self,
            unlocked: Optional[bool] = None,
            started_at: Optional[float] = None,
            total_fish_count: Optional[int] = None
        ) -> None:
        if unlocked is None:
            unlocked = False
        if started_at is None:
            started_at = 0
        if total_fish_count is None:
            total_fish_count = 0
        
        self.unlocked = unlocked
        self.started_at = started_at
        self.total_fish_count = total_fish_count

    def unlock(self) -> None:
        if not self.unlocked:
            self.unlocked = True
            self.started_at = datetime.now().timestamp()