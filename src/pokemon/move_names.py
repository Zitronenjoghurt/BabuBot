from fuzzywuzzy import process
from typing import Optional
from src.utils.file_operations import construct_path, file_to_dict

NAMES_FILE_PATH = construct_path("src/data/pokemon_move_names.json")

class PokemonMoveNames():
    _instance = None

    def __init__(self) -> None:
        if PokemonMoveNames._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of PokemonMoveNames.")
        self.names_map = file_to_dict(NAMES_FILE_PATH)
        self.names = list(self.names_map.keys())

    @staticmethod
    def get_instance() -> 'PokemonMoveNames':
        if PokemonMoveNames._instance is None:
            PokemonMoveNames._instance = PokemonMoveNames()
        return PokemonMoveNames._instance
    
    def match_name(self, name: str) -> Optional[str]:
        name = name.lower()
        result = process.extractOne(name, self.names, score_cutoff=40)
        if not result:
            return
        matched_name, score = result # type: ignore
        return self.names_map.get(matched_name, None)
    
    def match_name_extended(self, name: str) -> Optional[tuple[str, str, float]]:
        name = name.lower()
        result = process.extractOne(name, self.names, score_cutoff=10)
        if not result:
            return
        matched_name, score = result # type: ignore
        final_name = self.names_map.get(matched_name, None)
        if final_name is None:
            return None
        return (final_name, matched_name, score)