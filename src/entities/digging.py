from datetime import datetime
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class Digging(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["unlocked", "started_at", "reputation", "power_level", "speed_level", "capacity_level", "queue_level"]

    def __init__(
            self,
            unlocked: Optional[bool] = None,
            started_at: Optional[float] = None,
            reputation: Optional[int] = None,
            power_level: Optional[int] = None,
            speed_level: Optional[int] = None,
            capacity_level: Optional[int] = None,
            queue_level: Optional[int] = None
        ) -> None:
        if unlocked is None:
            unlocked = False
        if started_at is None:
            started_at = 0
        if reputation is None:
            reputation = 0
        if power_level is None:
            power_level = 1
        if speed_level is None:
            speed_level = 1
        if capacity_level is None:
            capacity_level = 1
        if queue_level is None:
            queue_level = 1

        self.unlocked = unlocked
        self.started_at = started_at
        self.reputation = reputation
        self.power_level = power_level
        self.speed_level = speed_level
        self.capacity_level = capacity_level
        self.queue_level = queue_level

    def unlock(self) -> None:
        if not self.unlocked:
            self.unlocked = True
            self.started_at = datetime.now().timestamp()