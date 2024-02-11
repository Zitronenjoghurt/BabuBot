from src.fishing.fish_rarity import FishRarity
from src.fishing.fish_type import FishType
from src.utils.maths import bell_curve_random

# An entry in the fish library of src/data/fish.json
class FishEntry():
    def __init__(
            self,
            id: str,
            name: str,
            scientific: str,
            type: FishType,
            color: str,
            emoji_id: str,
            rarity: FishRarity,
            price: int,
            min_size: float,
            max_size: float
        ) -> None:
        self.id = id
        self.name = name
        self.scientific = scientific
        self.type = type
        self.color = color
        self.emoji_id = emoji_id
        self.rarity = rarity
        self.price = price
        self.min_size = min_size
        self.max_size = max_size

    @staticmethod
    def from_dict(data: dict) -> 'FishEntry':
        id = data.get("id", "")
        name = data.get("name", "no name")
        scientific = data.get("scientific", "no scientific name")
        color = data.get("color", "#000000")
        emoji_id = data.get("emoji_id", "")
        price = data.get("price", 0)
        min_size = data.get("min_size", 0)
        max_size = data.get("max_size", 0)

        type = data.get("type", None)
        if type:
            type = FishType(type)
        else:
            raise ValueError(f"Invalid fish type {type}.")
        
        rarity = data.get("rarity", None)
        if rarity:
            rarity = FishRarity(rarity)
        else:
            raise ValueError(f"Invalid fish rarity {rarity}.")
        
        return FishEntry(
            id=id,
            name=name,
            scientific=scientific,
            type=type,
            color=color,
            emoji_id=emoji_id,
            rarity=rarity,
            price=price,
            min_size=min_size,
            max_size=max_size
        )
    
    def get_random_size(self) -> float:
        return bell_curve_random(self.min_size, self.max_size)