from typing import Optional
from src.constants.config import Config
from src.entities.abstract_database_entity import AbstractDatabaseEntity

CONFIG = Config.get_instance()

class DiggingQueueItem(AbstractDatabaseEntity):
    TABLE_NAME = "digging_queue"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "user_id", "item_id", "finish_stamp"]
    SAVED_PROPERTIES = ["user_id", "item_id", "finish_stamp", "created_stamp"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            user_id: Optional[str] = None,
            item_id: Optional[str] = None,
            finish_stamp: Optional[float] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        if user_id is None:
            user_id = ""
        if item_id is None:
            item_id = ""
        if finish_stamp is None:
            finish_stamp = 0
        
        self.user_id = user_id
        self.item_id = item_id
        self.finish_stamp = finish_stamp

    @staticmethod
    async def get_user_queue_items(user_id: str) -> list['DiggingQueueItem']:
        results: list['DiggingQueueItem'] = await DiggingQueueItem.findall(user_id=user_id, sort_key="finish_stamp")
        return results