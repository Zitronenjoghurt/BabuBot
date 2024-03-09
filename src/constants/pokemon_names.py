from difflib import get_close_matches
from typing import Optional
from src.utils.file_operations import construct_path, file_to_dict

NAMES_FILE_PATH = construct_path("src/data/pokemon_names.json")

class PokemonNames():
    _instance = None

    def __init__(self) -> None:
        if PokemonNames._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of PokemonNames.")
        self.names_map = file_to_dict(NAMES_FILE_PATH)
        self.names = list(self.names_map.keys())

    @staticmethod
    def get_instance() -> 'PokemonNames':
        if PokemonNames._instance is None:
            PokemonNames._instance = PokemonNames()
        return PokemonNames._instance
    
    def match_name(self, name: str) -> Optional[str]:
        name = name.lower()
        matched_names = get_close_matches(word=name, possibilities=self.names, n=1)
        if not matched_names:
            return
        return self.names_map.get(matched_names[0], None)