import src.items.types as TYPES

TYPE_REGISTRY = {
    "bait": TYPES.Bait,
    "rods": TYPES.FishingRod,
    "minerals": TYPES.Mineral,
    "treasures": TYPES.Treasure
}

def create_item(data: dict):
    category = data.get("category", None)
    if category is None:
        raise ValueError("Given item data has no category.")
    if category not in TYPE_REGISTRY:
        raise ValueError(f"Given item category {category} does not exist.")
    cls = TYPE_REGISTRY[category]
    try:
        item = cls(**data)
    except Exception as e:
        raise ValueError(f"An error occured while creating item of category {category}: {e}")
    return item