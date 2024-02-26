from typing import Optional
from src.digging.treasure_difficulty import TreasureDifficulty
from src.items.item import Item

class Treasure(Item):
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
            difficulty: int,
            buy_message: Optional[str] = None,
            needs_item: Optional[str] = None,
            image_name: Optional[str] = None
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
            buy_message=buy_message,
            needs_item=needs_item)
        
        if isinstance(difficulty, int):
            self.difficulty: TreasureDifficulty = TreasureDifficulty(difficulty)
        else:
            raise ValueError("Treasure difficulty has to be of type int.")

        if isinstance(image_name, str):
            self.image_name = image_name
        else:
            self.image_name = name