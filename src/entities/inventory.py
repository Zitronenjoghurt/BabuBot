from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.entities.inventory_item import InventoryItem

class Inventory(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["items"]
    SERIALIZE_CLASSES = {"items": InventoryItem}

    def __init__(
            self, 
            items: Optional[list[InventoryItem]] = None
        ) -> None:
        items = items if isinstance(items, list) else []
        self.items = items

    def has_item(self, id: str) -> bool:
        for item in self.items:
            if item.id == id:
                return True
        return False

    def item_count(self, id: str) -> int:
        count = 0
        for item in self.items:
            if item.id == id:
                if not item.unique:
                    return item.data.get("count", 0)
                count += 1
        return count
    
    def get_item(self, id: str) -> Optional[InventoryItem]:
        for item in self.items:
            if item.id == id:
                return item
        return None
    
    def add_item(self, item: InventoryItem, count: int = 1) -> None:
        if item.unique:
            self.items.append(item)
        else:
            inv_item = self.get_item(id=item.id)
            if isinstance(inv_item, InventoryItem):
                inv_item.add(count)
            else:
                self.items.append(item)
                item.add(count)

    def remove_item(self, id: str) -> None:
        self.items = [i for i in self.items if i.id != id]

    def consume_item(self, id: str, amount: int = 1) -> tuple[bool, str]:
        item = self.get_item(id=id)
        if not isinstance(item, InventoryItem):
            return False, "You dont have this item."
        if item.unique:
            self.remove_item(id=id)
            return True, ""
        else:
            item_count = item.data.get("count", 0)
            if item_count > amount:
                item.data["count"] -= amount
                return True, ""
            if item_count < amount:
                return False, f"You only have `{item_count}x`"
            self.remove_item(id=id)
            return True, ""
        
    def map_items_by_id_and_count(self) -> dict[str, int]:
        data = {}
        for item in self.items:
            if item.id not in data:
                data[item.id] = 0
            count = item.data.get("count", 1)
            data[item.id] += count
        return data