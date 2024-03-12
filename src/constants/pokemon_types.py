from typing import Optional
from src.constants.emoji_index import EmojiIndex
from src.utils.file_operations import construct_path, file_to_dict

TYPES_FILE_PATH = construct_path("src/data/pokemon_types.json")

EMOJI_INDEX = EmojiIndex.get_instance()

class PokemonTypes():
    _instance = None

    def __init__(self) -> None:
        if PokemonTypes._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of PokemonTypes.")
        self.type_effects = file_to_dict(TYPES_FILE_PATH)
        self.type_effects_values = list(self.type_effects.values())
        self.type_index = {typing: i for i, typing in enumerate(self.type_effects.keys())}
        self.types = list(self.type_effects.keys())
        self.type_count = len(self.types)

    @staticmethod
    def get_instance() -> 'PokemonTypes':
        if PokemonTypes._instance is None:
            PokemonTypes._instance = PokemonTypes()
        return PokemonTypes._instance

    def get_effective_against_type_values(self, type: str) -> list[float]:
        type = type.lower()
        index = self.type_index.get(type, None)
        if not isinstance(index, int):
            raise ValueError(f"Pokemon type {type} does not exist.")
        return [value[index] for value in self.type_effects_values]
    
    def get_typing_effectiveness(self, typing: list[str]) -> 'TypingEffectiveness':
        values = [1] * self.type_count
        for type in typing:
            if type not in self.types:
                continue
            type_values = self.get_effective_against_type_values(type=type)
            values = [values[i] * type_values[i] for i in range(self.type_count)]
        effectiveness = [v for v in zip(self.types, values)]
        return TypingEffectiveness(type_effectiveness=effectiveness)
    
class TypingEffectiveness():
    def __init__(self, type_effectiveness: list[tuple[str, float]]) -> None:
        self.type_effectiveness = type_effectiveness
        self.super_effective, self.effective, self.neutral, self.resistant, self.super_resistant, self.immune = self.format_and_group()

    def format_and_group(self) -> list[str]:
        groups = [[] for _ in range(6)]
        for effectiveness in self.type_effectiveness:
            type = effectiveness[0]
            value = effectiveness[1]
            index = 0
            if value >= 4:
                index = 0
            elif value >= 2:
                index = 1
            elif value == 1:
                index = 2
            elif value == 0:
                index = 5
            elif value <= 1/4:
                index = 4
            elif value <= 1/2:
                index = 3
            groups[index].append(EMOJI_INDEX.get_emoji(type))
        return ["".join(group) if len(group) > 0 else "*None*" for group in groups]