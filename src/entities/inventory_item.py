from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class InventoryItem(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["id", "unique", "data"]

    def __init__(
            self, 
            id: str,
            unique: bool,
            data: dict
        ) -> None:
        self.id = id
        self.unique = unique
        self.data = data

    def add(self, amount: int) -> None:
        if self.unique:
            return
        if "count" not in self.data:
            self.data["count"] = 0
        self.data["count"] += amount