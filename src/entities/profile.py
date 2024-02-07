from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

FIELDS = ["name", "pronouns", "age", "location", "about_me"]
INLINE_FIELDS = ["name", "age", "pronouns", "location"]
PARAGRAPH_FIELDS = ["about_me"]

class Profile(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["name", "age", "pronouns", "location", "about_me", "views"]

    def __init__(
            self, 
            name: Optional[str] = None, 
            age: Optional[str] = None, 
            pronouns: Optional[str] = None,
            location: Optional[str] = None,
            about_me: Optional[str] = None,
            views: Optional[int] = None
        ) -> None:
        if name is None:
            name = ""
        if age is None:
            age = ""
        if pronouns is None:
            pronouns = ""
        if location is None:
            location = ""
        if about_me is None:
            about_me = ""
        if views is None:
            views = 0

        self.name = str(name)
        self.age = str(age)
        self.pronouns = str(pronouns)
        self.location = str(location)
        self.about_me = str(about_me)
        self.views = int(views)

    def is_empty(self) -> bool:
        checks = [
            self.name == "",
            self.age == "",
            self.pronouns == "",
            self.location == "",
            self.about_me == ""
        ]
        return all(checks)

    def clear(self) -> None:
        self.name = ""
        self.age = ""
        self.pronouns = ""
        self.location = ""
        self.about_me = ""

    def count_view(self) -> None:
        self.views += 1

    def generate_fields(self) -> list[dict]:
        fields = []
        for field in FIELDS:
            value = getattr(self, field)
            if len(value) == 0:
                continue
            fields.append({
                "name": field.capitalize().replace("_", " "),
                "value": f"```{value}```" if field in PARAGRAPH_FIELDS else f"`{value}`",
                "inline": field in INLINE_FIELDS
            })
        return fields