from typing import Optional
from src.items.item import Item

class Bait(Item):
    def __init__(
            self, 
            name: str, 
            unique: bool, 
            id: str, 
            display_name: str,
            color: str, 
            description: str, 
            use: str, 
            category: str, 
            emoji_id: str, 
            price: int, 
            max_count: int, 
            data: dict,
            requirements: list[str],
            needs_item: Optional[str] = None
        ) -> None:
        super().__init__(
            name=name, 
            unique=unique, 
            id=id, 
            display_name=display_name, 
            color=color, 
            description=description, 
            use=use, 
            category=category, 
            emoji_id=emoji_id, 
            price=price, 
            max_count=max_count, 
            data=data,
            requirements=requirements,
            needs_item=needs_item)