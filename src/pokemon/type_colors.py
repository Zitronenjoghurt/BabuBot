from src.utils.file_operations import construct_path, file_to_dict

COLORS_FILE_PATH = construct_path("src/data/pokemon_type_colors.json")

class PokemonTypeColors():
    _instance = None

    def __init__(self) -> None:
        if PokemonTypeColors._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of PokemonTypeColors.")
        self.colors = file_to_dict(COLORS_FILE_PATH)

    @staticmethod
    def get_instance() -> 'PokemonTypeColors':
        if PokemonTypeColors._instance is None:
            PokemonTypeColors._instance = PokemonTypeColors()
        return PokemonTypeColors._instance
    
    def get_color(self, type: str) -> str:
        type = type.lower()
        return self.colors.get(type, "#000000")