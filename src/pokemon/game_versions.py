from dataclasses import dataclass
from typing import Optional
from src.utils.file_operations import construct_path, file_to_dict

VERSIONS_FILE_PATH = construct_path("src/data/pokemon_game_versions.json")

@dataclass
class PokemonVersionGroup:
    id: str
    name: str
    gen: int

class PokemonGameVersions():
    _instance = None

    def __init__(self) -> None:
        if PokemonGameVersions._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of PokemonGameVersions.")
        data = file_to_dict(VERSIONS_FILE_PATH)
        self.id_version_map: dict[str, PokemonVersionGroup]   = {}
        self.name_version_map: dict[str, PokemonVersionGroup] = {}
        try:
            for id, version_data in data.items():
                version_data["id"] = id
                version = PokemonVersionGroup(**version_data)
                self.id_version_map[id.lower()] = version
                self.name_version_map[version.name.lower()] = version
        except Exception as e:
            raise RuntimeError(f"An error occured while initializing PokemonGameVersions: {e}")

    @staticmethod
    def get_instance() -> 'PokemonGameVersions':
        if PokemonGameVersions._instance is None:
            PokemonGameVersions._instance = PokemonGameVersions()
        return PokemonGameVersions._instance
    
    def get_by_id(self, id: str) -> Optional[PokemonVersionGroup]:
        id = id.lower()
        return self.id_version_map.get(id, None)
    
    def get_by_name(self, name: str) -> Optional[PokemonVersionGroup]:
        name = name.lower()
        return self.name_version_map.get(name, None)