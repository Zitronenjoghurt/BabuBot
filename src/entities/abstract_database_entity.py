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

    async def save(self, return_changed_fields: bool = False) -> Optional[dict]:
        data = self.to_dict()
        save_data = {key: value for key, value in data.items() if key in self.SAVED_PROPERTIES}
        if self.id is None:
            self.id = DB.insert(table_name=self.TABLE_NAME, data=save_data)
        else:
            return DB.update(table_name=self.TABLE_NAME, entity_id=self.id, data=save_data, return_changed_fields=return_changed_fields)

    @classmethod
    async def find(cls, **kwargs) -> Any:
        result = DB.find(table_name=cls.TABLE_NAME, **kwargs)
        if not result:
            return None
        if not result:
            return None
        return map_entity_from_result(cls=cls, result=result)

    @classmethod
    async def findall(cls, sort_key: Optional[str] = None, descending: bool = True, limit: Optional[int] = None, page: int = 1, **kwargs) -> Any:
        results = DB.findall(table_name=cls.TABLE_NAME, sort_key=sort_key, descending=descending, limit=limit, page=page, **kwargs)
        if not results:
            return []
        
        entities = []
        for result in results:
            entity = map_entity_from_result(cls=cls, result=result)
            if entity:
                entities.append(entity)
        return entities
    
    @classmethod
    async def find_containing(cls, key: str, values: list) -> Any:
        result = DB.find_containing(table_name=cls.TABLE_NAME, key=key, values=values)
        if not result:
            return None
        return map_entity_from_result(cls=cls, result=result)
    
    @classmethod
    async def findall_containing(cls, key: str, values: list, sort_key: Optional[str] = None, descending: bool = True, limit: Optional[int] = None, page: int = 1) -> Any:
        results = DB.findall_containing(table_name=cls.TABLE_NAME, key=key, values=values, sort_key=sort_key, descending=descending, limit=limit, page=page)
        if not results:
            return []
        
        entities = []
        for result in results:
            entity = map_entity_from_result(cls=cls, result=result)
            if entity:
                entities.append(entity)
        return entities
    
    # Return entity if exists, otherwise create a new one
    @classmethod
    async def load(cls, **kwargs) -> Any:
        entity = await cls.find(**kwargs)
        if not entity:
            return cls.from_dict(kwargs)
        return entity
    
    @classmethod
    async def get_earliest_entity(cls) -> Any:
        return await cls.findall(sort_key='created_stamp', descending=False, limit=1)
    
    @classmethod
    async def get_earliest_created_stamp(cls) -> Optional[float]:
        entities = await cls.get_earliest_entity()
        if not entities:
            return None
        return entities[0].created_stamp
    
def map_entity_from_result(cls, result: tuple[int, str]) -> Any:
    id = int(result[0])
    data = json.loads(result[1])
    data["id"] = id
    return cls.from_dict(data=data)