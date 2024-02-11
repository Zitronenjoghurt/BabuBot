from typing import Optional
from src.items.item import Item
from src.items.item_factory import create_item
from src.items.types import Bait
from src.utils.file_operations import construct_path, file_to_dict

DATA_FILE_PATH = construct_path("src/data/items.json")
IMAGE_PATH = "src/assets/{category}/{name}.png"

class ItemLibrary():
    _instance = None

    def __init__(self) -> None:
        if ItemLibrary._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of ItemLibrary.")
        self.items_by_name = {}
        self.items_by_display_name = {}
        self.items_by_id = {}
        self.items_by_category = {}
        self._initialize_items()

    def _initialize_items(self) -> None:
        item_data = file_to_dict(DATA_FILE_PATH)
        for name, data in item_data.items():
            data["name"] = name
            item: Item = create_item(data=data)
            self.items_by_name[name] = item
            self.items_by_display_name[item.display_name.lower()] = item
            self.items_by_id[item.id.lower()] = item

            if item.category not in self.items_by_category:
                self.items_by_category[item.category] = []
            self.items_by_category[item.category].append(item)

    @staticmethod
    def get_instance() -> 'ItemLibrary':
        if ItemLibrary._instance is None:
            ItemLibrary._instance = ItemLibrary()
        return ItemLibrary._instance
    
    def items_from_id_and_count(self, data: dict[str, int], category: Optional[str] = None) -> list[Item]:
        items = []
        for id, count in data.items():
            item = self.get_item_by_id(id)
            if not item:
                continue
            if category and item.category != category.lower():
                continue
            item.data["count"] = count
            items.append(item)
        return items
    
    def get_categories(self) -> list[str]:
        return list(self.items_by_category.keys())
    
    def find(self, identifier: str) -> Optional[Item]:
        if identifier.lower() in self.items_by_id:
            return self.items_by_id[identifier.lower()]
        if identifier.lower() in self.items_by_display_name:
            return self.items_by_display_name[identifier.lower()]
        if identifier in self.items_by_name:
            return self.items_by_name[identifier]
        return None
    
    def get_item_by_id(self, id: str) -> Optional[Item]:
        id = id.lower()
        if id not in self.items_by_id:
            return None
        return self.items_by_id[id]
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        if name not in self.items_by_name:
            return None
        return self.items_by_name[name]
    
    def get_items_by_category(self, category: str) -> list[Item]:
        if category not in self.items_by_category:
            return []
        return self.items_by_category[category]
    
    def get_available_bait(self) -> list[str]:
        baits: list[Bait] = self.get_items_by_category("bait") # type: ignore
        bait_by_level = []
        for bait in baits:
            bait_by_level.append((bait.bait_level, bait.display_name))

        bait_by_level_sorted = sorted(bait_by_level, key=lambda x: x[0])

        bait_names = [bait[1] for bait in bait_by_level_sorted]
        return bait_names