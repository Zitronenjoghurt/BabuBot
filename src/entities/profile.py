from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class Profile(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["name", "age", "pronouns", "views"]
    
    FIELDS = ["name", "pronouns", "age"]
    INLINE_FIELDS = ["name", "age", "pronouns"]

    def __init__(
            self, 
            name: Optional[str] = None, 
            age: Optional[str] = None, 
            pronouns: Optional[str] = None,
            views: Optional[int] = None
        ) -> None:
        if name is None:
            name = ""
        if age is None:
            age = ""
        if pronouns is None:
            pronouns = ""
        if views is None:
            views = 0

        self.name = str(name)
        self.age = str(age)
        self.pronouns = str(pronouns)
        self.views = int(views)

    def count_view(self) -> None:
        self.views += 1

    def generate_fields(self) -> list[dict]:
        fields = []
        for field in self.FIELDS:
            value = getattr(self, field)
            if len(value) == 0:
                continue
            fields.append({
                "name": field.capitalize(),
                "value": f"`{value}`",
                "inline": field in self.INLINE_FIELDS
            })
        return fields