from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class RocketLaunchStatus(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["name", "abbreviation", "description"]

    def __init__(
            self, 
            name: Optional[str] = None,
            abbreviation: Optional[str] = None,
            description: Optional[str] = None
        ) -> None:
        self.name = name if isinstance(name, str) else "No Status"
        self.abbreviation = abbreviation if isinstance(abbreviation, str) else "No Status"
        self.description = description if isinstance(description, str) else "No Status"

    @staticmethod
    def from_api_data(data: dict) -> 'RocketLaunchStatus':
        name = data.get("name", None)
        abbreviation = data.get("abbrev", None)
        description = data.get("description", None)
        return RocketLaunchStatus(name=name, abbreviation=abbreviation, description=description)