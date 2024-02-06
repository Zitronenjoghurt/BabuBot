from datetime import datetime
import json
from typing import Any, Optional
from src.database.database import Database
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

DB = Database.get_instance()

class AbstractDatabaseEntity(AbstractSerializableEntity):
    TABLE_NAME = ""
    SERIALIZED_PROPERTIES = ["id", "created_stamp"]
    SAVED_PROPERTIES = ["created_stamp"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None
        ) -> None:
        if created_stamp is None:
            created_stamp = datetime.now().timestamp()

        self.id = id
        self.created_stamp = created_stamp

    def save(self) -> None:
        data = self.to_dict()
        save_data = {key: value for key, value in data.items() if key in self.SAVED_PROPERTIES}
        if self.id is None:
            self.id = DB.insert(table_name=self.TABLE_NAME, data=save_data)
        else:
            DB.update(table_name=self.TABLE_NAME, entity_id=self.id, data=save_data)

    @classmethod
    def find(cls, **kwargs) -> Any:
        result = DB.find(table_name=cls.TABLE_NAME, **kwargs)
        if not result:
            return None
        
        id = int(result[0])
        data = json.loads(result[1])
        data["id"] = id
        
        return cls.from_dict(data=data)

    @classmethod
    def findall(cls, sort_key: Optional[str] = None, descending: bool = True, limit: Optional[int] = None, page: int = 1, **kwargs) -> Any:
        results = DB.findall(table_name=cls.TABLE_NAME, sort_key=sort_key, descending=descending, limit=limit, page=page, **kwargs)
        if not results:
            return []
        
        entities = []
        for result in results:
            id = int(result[0])
            data = json.loads(result[1])
            data["id"] = id
            entities.append(cls.from_dict(data=data))
        return entities
    
    # Return entity if exists, otherwise create a new one
    @classmethod
    def load(cls, **kwargs) -> Any:
        entity = cls.find(**kwargs)
        if not entity:
            return cls.from_dict(kwargs)
        return entity