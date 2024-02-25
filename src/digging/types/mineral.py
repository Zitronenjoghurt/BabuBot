from typing import Optional
from src.digging.treasure import Treasure

class Mineral(Treasure):
    def __init__(
        self, 
        name: str, 
        type: str, 
        difficulty: int,
        display_name: str,
        description: str,
        color: str,
        emoji_id: str,
        image_name: Optional[str]
    ) -> None:
        super().__init__(name, type, difficulty, display_name, description, color, emoji_id, image_name)