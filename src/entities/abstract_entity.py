import json
from numbers import Number
from typing import Any, Optional
from src.database.database import Database
from src.utils.dict_operations import retrieve_data

DB = Database.get_instance()

class AbstractEntity():
    TABLE_NAME = ""

    def __init__(self, id: Optional[int] = None) -> None:
        self.id = id

    def to_dict(self) -> dict:
        return {}
    
    @staticmethod
    def from_dict(data: dict) -> 'AbstractEntity':
        data = retrieve_data(data, ["id"])
        return AbstractEntity(**data)

    def save(self) -> None:
        data = self.to_dict()
        if self.id is None:
            self.id = DB.insert(table_name=self.TABLE_NAME, data=data)
        else:
            DB.update(table_name=self.TABLE_NAME, entity_id=self.id, data=data)

    @classmethod
    def find(cls, **kwargs) -> Any:
        entities = cls.findall(**kwargs)
        if len(entities) > 0:
            return entities[0]

    @classmethod
    def findall(cls, **kwargs) -> Any:
        results = DB.find(table_name=cls.TABLE_NAME, **kwargs)
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