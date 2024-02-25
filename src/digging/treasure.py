from typing import Optional
from src.digging.treasure_difficulty import TreasureDifficulty

class Treasure():
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
        self.name = name
        self.type = type
        self.display_name = display_name
        self.description = description
        self.color = color
        self.emoji_id = emoji_id

        if isinstance(difficulty, int):
            self.difficulty: TreasureDifficulty = TreasureDifficulty(difficulty)
        else:
            raise ValueError("Treasure difficulty has to be of type int.")

        if isinstance(image_name, str):
            self.image_name = image_name
        else:
            self.image_name = name