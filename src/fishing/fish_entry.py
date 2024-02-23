from src.fishing.fish_category import FishCategory
from src.fishing.fish_rarity import FishRarity
from src.fishing.fish_type import FishType
from src.utils.maths import bell_curve_random

IMAGE_PATH = "src/assets/fishes/{id}.png"

RARITY_COLORS = {
    FishRarity.COMMON: "#41A85F",
    FishRarity.UNCOMMON: "#2C82C9",
    FishRarity.RARE: "#9365B8",
    FishRarity.LEGENDARY: "#FAC51C",
    FishRarity.MYTHICAL: "#F73D2A",
    FishRarity.GODLY: "#FA11EA"
}

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
            max_size: float,
            description: str,
            category: FishCategory,
            invisible: bool,
            followup_content: str
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
        self.description = description
        self.category = category
        self.invisible = invisible
        self.followup_content = followup_content

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
        description = data.get("description", 0)
        invisible = data.get("invisible", False)
        followup_content = data.get("followup_content", "")

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
        
        category = data.get("category", None)
        if category:
            category = FishCategory(category)
        else:
            category = FishCategory.REGULAR
        
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
            max_size=max_size,
            description=description,
            category=category,
            invisible=invisible,
            followup_content=followup_content
        )
    
    def get_random_size(self) -> float:
        return bell_curve_random(self.min_size, self.max_size)
    
    def get_rarity_color(self) -> str:
        return RARITY_COLORS[self.rarity]
    
    def get_emoji(self) -> str:
        return f"<:{self.id}:{self.emoji_id}>"
    
    def get_image_path(self) -> str:
        return IMAGE_PATH.format(id=self.id)
    
    def get_image_file_name(self) -> str:
        return f"{self.id}.png"
    
    def get_image_url(self) -> str:
        image_file_name = self.get_image_file_name()
        return f"attachment://{image_file_name}"
    
    def get_size_range(self) -> str:
        return f"{self.min_size}-{self.max_size}cm"
    
    def size_classification(self, size: float) -> str:
        size_labels = ['XXXS', 'XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
        total_range = self.max_size - self.min_size
        segment = total_range / (len(size_labels) - 1) 

        index = int((size - self.min_size) / segment)
        index = max(0, min(index, len(size_labels) - 1))

        return size_labels[index]