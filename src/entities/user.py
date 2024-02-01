from numbers import Number
from typing import Optional
from src.entities.abstract_entity import AbstractEntity
from src.utils.dict_operations import retrieve_data

class User(AbstractEntity):
    TABLE_NAME = "users"

    def __init__(self, id: Optional[int] = None, userid: Optional[str] = None, message_count: Optional[int] = None) -> None:
        super().__init__(id=id)
        if userid is None:
            userid = ""
        if message_count is None:
            message_count = 0

        self.userid = str(userid)
        self.message_count = int(message_count)

    def to_dict(self) -> dict:
        data = {
            "userid": self.userid,
            "message_count": self.message_count
        }
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'AbstractEntity':
        data = retrieve_data(data, ["id", "userid", "message_count"])
        return User(**data)
    
    def count_message(self) -> None:
        self.message_count += 1