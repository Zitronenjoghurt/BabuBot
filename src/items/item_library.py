from typing import Optional
from src.items.item import Item
from src.items.item_factory import create_item
from src.utils.file_operations import construct_path, file_to_dict

DATA_FILE_PATH = construct_path("src/data/items.json")

class ItemLibrary():
    _instance = None

    def __init__(self) -> None:
        if ItemLibrary._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of ItemLibrary.")
        self.items_by_name = {}
        self.items_by_id = {}
        self._initialize_items()

    def _initialize_items(self) -> None:
        item_data = file_to_dict(DATA_FILE_PATH)
        for name, data in item_data.items():
            data["name"] = name
            item = create_item(data=data)
            self.items_by_name[name] = item
            self.items_by_id[item.id] = item

    @staticmethod
    def get_instance() -> 'ItemLibrary':
        if ItemLibrary._instance is None:
            ItemLibrary._instance = ItemLibrary()
        return ItemLibrary._instance
    
    def get_item_by_id(self, id: str):
        if id not in self.items_by_id:
            return None
        return self.items_by_id[id]
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        if name not in self.items_by_name:
            return None
        return self.items_by_name[name]