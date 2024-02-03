from typing import Optional
from src.entities.abstract_database_entity import AbstractDatabaseEntity

class Feedback(AbstractDatabaseEntity):
    TABLE_NAME = "feedback"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "creator_id", "text"]
    SAVED_PROPERTIES = ["created_stamp", "creator_id", "text"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            creator_id: Optional[str] = None,
            text: Optional[str] = None
        ) -> None:
        super().__init__(id, created_stamp)

        self.creator_id = str(creator_id)
        self.text = str(text)