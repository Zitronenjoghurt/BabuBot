from datetime import datetime, timedelta
from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.utils.discord_time import relative_time
from src.utils.time_operations import get_todays_midnight, get_tomorrows_midnight

DAILY_AMOUNT = 200
STREAK_MULTIPLIER = 0.025

# If your last daily was before this threshold you will lose your streak
STREAK_THRESHOLD_DAYS = 3 

class Economy(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["currency", "last_daily_stamp", "daily_streak", "received_log", "sent_log"]

    def __init__(
            self, 
            currency: Optional[int] = None,
            last_daily_stamp: Optional[float] = None,
            daily_streak: Optional[int] = None,
            received_log: Optional[list] = None,
            sent_log: Optional[list] = None
        ) -> None:
        if currency is None:
            currency = 0
        if last_daily_stamp is None:
            last_daily_stamp = 0
        if daily_streak is None:
            daily_streak = 0
        if received_log is None:
            received_log = []
        if sent_log is None:
            sent_log = []

        self.currency = currency
        self.last_daily_stamp = last_daily_stamp
        self.daily_streak = daily_streak

        # A list of tuple[userid, amount, timestamp]
        self.received_log: list[tuple[str, int, float]] = received_log
        self.sent_log: list[tuple[str, int, float]] = sent_log

    def add_currency(self, amount: int) -> None:
        self.currency += amount

    def remove_currency(self, amount: int) -> bool:
        if amount > self.currency:
            return False
        self.currency -= amount
        return True
    
    def can_do_daily(self) -> bool:
        todays_midnight = get_todays_midnight().timestamp()

        if todays_midnight > self.last_daily_stamp:
            return True
        return False
    
    def will_lose_streak(self) -> bool:
        if self.last_daily_stamp == 0:
            return False
        
        last_daily = datetime.fromtimestamp(self.last_daily_stamp)
        now = datetime.now()

        difference = now - last_daily

        if difference >= timedelta(days=STREAK_THRESHOLD_DAYS):
            return True
        return False
    
    def do_daily(self) -> tuple[bool, int]:
        if not self.can_do_daily():
            return False, 0
        
        if self.will_lose_streak():
            self.daily_streak = 0
        
        bonus = STREAK_MULTIPLIER * self.daily_streak * DAILY_AMOUNT
        total = int(DAILY_AMOUNT + bonus)
        self.add_currency(total)
        self.last_daily_stamp = datetime.now().timestamp()

        self.daily_streak += 1
        
        return True, total
    
    def when_next_daily(self) -> datetime:
        if self.can_do_daily():
            return get_todays_midnight()
        return get_tomorrows_midnight()
    
    def next_daily_discord_stamp(self) -> str:
        next_daily = self.when_next_daily()
        return relative_time(int(next_daily.timestamp()))
    
    def send_money(self, amount: int, receiver_id: str) -> bool:
        if amount > self.currency:
            return False
        
        self.remove_currency(amount=amount)
        self.sent_log.append((receiver_id, amount, datetime.now().timestamp()))
        return True
    
    def receive_money(self, amount: int, sender_id: str) -> None:
        self.add_currency(amount=amount)
        self.received_log.append((sender_id, amount, datetime.now().timestamp()))