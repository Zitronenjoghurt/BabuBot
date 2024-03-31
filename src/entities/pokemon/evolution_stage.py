from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.entities.pokemon.evolution_details import EvolutionDetails
from src.utils.dict_operations import get_safe_from_path

class EvolutionStage(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["species", "next", "methods"]
    SERIALIZE_CLASSES = {}

    def __init__(
            self,
            species: Optional[str] = None,
            next: Optional[list['EvolutionStage']] = None,
            methods: Optional[list[EvolutionDetails]] = None
        ) -> None:
        self.species = species if isinstance(species, str) else "Unknown"
        self.next = next if isinstance(next, list) else []
        self.methods = methods if isinstance(methods, list) else []

    @staticmethod
    async def from_api_data(data: dict) -> 'EvolutionStage':
        species = get_safe_from_path(data, ["species", "name"])

        details_data_list = data.get("evolution_details", [])
        if not isinstance(details_data_list, list):
            details_data_list = []

        details = []
        for details_data in details_data_list:
            details.append(EvolutionDetails.from_api_data(data=details_data))

        evolves_to = data.get("evolves_to", [])
        if not isinstance(evolves_to, list):
            evolves_to = []
        
        next_stages = []
        for evolution_data in evolves_to:
            next_stages.append(await EvolutionStage.from_api_data(data=evolution_data))

        return EvolutionStage(
            species=species,
            next=next_stages,
            methods=details
        )
    
    def has_next_stages(self) -> bool:
        return len(self.next) > 0
    
    def get_methods_string(self) -> str:
        if len(self.methods) == 0:
            return "no known methods"
        
        method_strings = []
        for method in self.methods:
            if not isinstance(method, EvolutionDetails):
                continue
            string = method.to_string()
            if isinstance(string, str):
                method_strings.append(f"> {string}")

        if len(method_strings) == 0:
            return "no known methods"
        return "\n".join(method_strings)

# Ensures that EvolutionStage is fully initialized and then put into the serialize classes constant
EvolutionStage.SERIALIZE_CLASSES = {"next": EvolutionStage, "methods": EvolutionDetails}