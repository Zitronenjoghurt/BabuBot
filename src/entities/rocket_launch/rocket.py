from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class Rocket(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["name", "family", "full_name", "variant"]

    def __init__(
            self, 
            name: Optional[str] = None,
            family: Optional[str] = None,
            full_name: Optional[str] = None,
            variant: Optional[str] = None
        ) -> None:
        self.name = name if isinstance(name, str) else "No Rocket"
        self.family = family if isinstance(family, str) else "No Rocket"
        self.full_name = full_name if isinstance(full_name, str) else "No Rocket"
        self.variant = variant if isinstance(variant, str) else "No Rocket"

    @staticmethod
    def from_api_data(data: dict) -> 'Rocket':
        configuration_data = data.get("configuration", {})
        if not isinstance(configuration_data, dict):
            configuration_data = {}

        name = configuration_data.get("name", None)
        family = configuration_data.get("family", None)
        full_name = configuration_data.get("full_name", None)
        variant = configuration_data.get("variant", None)
        return Rocket(name=name, family=family, full_name=full_name, variant=variant)