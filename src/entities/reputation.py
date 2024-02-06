from datetime import datetime
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.utils.discord_time import relative_time
from src.utils.time_operations import get_todays_midnight, get_tomorrows_midnight

class Reputation(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["points_given", "points_received", "last_rep_stamp", "log_given", "log_received"]

    def __init__(
            self, 
            points_given: Optional[int] = None,
            points_received: Optional[float] = None,
            last_rep_stamp: Optional[float] = None,
            log_given: Optional[list] = None,
            log_received: Optional[list] = None
        ) -> None:
        if points_given is None:
            points_given = 0
        if points_received is None:
            points_received = 0
        if last_rep_stamp is None:
            last_rep_stamp = 0
        if log_given is None:
            log_given = []
        if log_received is None:
            log_received = []

        self.points_given = points_given
        self.points_received = points_received
        self.last_rep_stamp = last_rep_stamp

        # Maps userid to timestamp
        self.log_given: list[tuple[str, float]] = log_given
        self.log_received: list[tuple[str, float]] = log_received

    def rep_to(self, userid: str) -> None:
        if self.can_do_rep():
            self.points_given += 1
            current_timestamp = datetime.now().timestamp()
            self.last_rep_stamp = current_timestamp
            self.log_given.append((userid, current_timestamp))

    def rep_from(self, userid: str) -> None:
        self.points_received += 1
        self.log_received.append((userid, datetime.now().timestamp()))

    def can_do_rep(self) -> bool:
        todays_midnight = get_todays_midnight().timestamp()

        if todays_midnight > self.last_rep_stamp:
            return True
        return False

    def when_next_rep(self) -> datetime:
        if self.can_do_rep():
            return get_todays_midnight()
        return get_tomorrows_midnight()
    
    def next_rep_discord_stamp(self) -> str:
        next_rep = self.when_next_rep()
        return relative_time(int(next_rep.timestamp()))