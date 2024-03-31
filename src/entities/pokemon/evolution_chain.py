import re
from typing import Optional
from src.apis.pokemon_api import PokemonApi
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.pokemon.evolution_stage import EvolutionStage

POKEMON_API = PokemonApi.get_instance()

class EvolutionChain(AbstractDatabaseEntity):
    TABLE_NAME = "pokemon_evo_chains"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "root", "chain_id"]
    SERIALIZE_CLASSES = {"root": EvolutionStage}
    SAVED_PROPERTIES = ["created_stamp", "root", "chain_id"]

    def __init__(
            self,
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            chain_id: Optional[int] = None,
            root: Optional[EvolutionStage] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        self.chain_id = chain_id if isinstance(chain_id, int) else 0
        self.root = root if isinstance(root, EvolutionStage) else None

    @staticmethod
    async def from_api_data(data: dict, id: int) -> 'EvolutionChain':
        root = await EvolutionStage.from_api_data(data=data)
        return EvolutionChain(chain_id=id, root=root)
    
    @staticmethod
    async def fetch(chain_id: int) -> Optional['EvolutionChain']:
        chain = await EvolutionChain.find(chain_id=chain_id)
        if isinstance(chain, EvolutionChain):
            return chain
        
        data = await POKEMON_API.get_evolution_chain_data(id=chain_id)
        if not isinstance(data, dict):
            return
        chain_data = data.get("chain", None)
        if not isinstance(chain_data, dict):
            return

        chain = await EvolutionChain.from_api_data(id=chain_id, data=chain_data)
        await chain.save()
        return chain
    
    def has_stages(self) -> bool:
        if not isinstance(self.root, EvolutionStage):
            return False
        return self.root.has_next_stages()
    
    def get_fields(self) -> list[tuple[str, str]]:
        if not isinstance(self.root, EvolutionStage):
            return []
        
        fields = []
        fields.append((f"{format_name(self.root.species)}", "**`Base Stage`**"))

        next = self.root.next
        stage_number = 1
        while len(next) > 0:
            next_stages = []
            for stage in next:
                fields.append((f"({stage_number}) {format_name(stage.species)}", f"{stage.get_methods_string()}"))
                next_stages.extend(stage.next)
            next = next_stages
            stage_number += 1

        return fields
    
def format_name(string: str) -> str:
    parts = string.split('-')
    capitalized_parts = [part.capitalize() for part in parts]
    return ' '.join(capitalized_parts)