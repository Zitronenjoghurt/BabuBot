from typing import Optional
from src.apis.pokemon_api import PokemonApi
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.utils.dict_operations import get_safe_from_path
from src.utils.string_operations import last_integer_from_url

POKEMON_API = PokemonApi.get_instance()

NAMES_LANGUAGES = ["en", "de", "fr", "ja", "roomaji"]

class PokemonAbility(AbstractDatabaseEntity):
    TABLE_NAME = "pokemon_abilities"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "name", "effect", "effect_short", "generation", "pokemon", "localized_names"]
    SAVED_PROPERTIES = ["created_stamp", "name", "effect", "effect_short", "generation", "pokemon", "localized_names"]

    def __init__(
            self,
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            name: Optional[str] = None,
            effect: Optional[str] = None,
            effect_short: Optional[str] = None,
            generation: Optional[int] = None,
            pokemon: Optional[list[tuple[str, bool]]] = None,
            localized_names: Optional[dict] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        self.name = name if isinstance(name, str) else "Missing Name"
        self.effect = effect if isinstance(effect, str) else "Missing Effect"
        self.effect_short = effect_short if isinstance(effect_short, str) else "Missing Short Effect"
        self.generation = generation if isinstance(generation, int) else None
        self.pokemon = pokemon if isinstance(pokemon, list) else []
        self.localized_names = localized_names if isinstance(localized_names, dict) else {}

    @staticmethod
    def from_api_data(data: dict) -> 'PokemonAbility':
        name = data.get("name", None)
        
        effect_entries = data.get("effect_entries", [])
        if not isinstance(effect_entries, list):
            effect_entries = []
        effect, effect_short = parse_effects(effect_entries=effect_entries)

        generation_url = get_safe_from_path(data, ["generation", "url"])
        if isinstance(generation_url, str):
            generation = last_integer_from_url(url=generation_url)
        else:
            generation = None

        pokemon_data = data.get("pokemon", [])
        if not isinstance(pokemon_data, list):
            pokemon_data = []
        pokemon = parse_pokemon(pokemon_data=pokemon_data)

        names_data = data.get("names", [])
        if not isinstance(names_data, list):
            names_data = []
        localized_names = parse_localized_names(names=names_data)

        return PokemonAbility(
            name=name,
            effect=effect,
            effect_short=effect_short,
            generation=generation,
            pokemon=pokemon,
            localized_names=localized_names
        )
    
    @staticmethod
    async def fetch(name: str) -> Optional['PokemonAbility']:
        ability = await PokemonAbility.find(name=name)
        if isinstance(ability, PokemonAbility):
            return ability
        
        ability_data = await POKEMON_API.get_ability_data(name=name)
        if not isinstance(ability_data, dict):
            return None
        
        ability = PokemonAbility.from_api_data(data=ability_data)
        await ability.save()
        return ability

def parse_effects(effect_entries: list[dict]) -> tuple[str, str]:
    for entry in effect_entries:
        language = get_safe_from_path(entry, ["language", "name"])
        if language == "en":
            long = entry.get("effect", "")
            short = entry.get("short_effect", "")
            return long, short
    return "", ""

def parse_pokemon(pokemon_data: list[dict]) -> list[tuple[str, bool]]:
    pokemon_and_hidden = []

    for pokemon in pokemon_data:
        name = get_safe_from_path(pokemon, ["pokemon", "name"])
        if not isinstance(name, str):
            continue
        is_hidden = pokemon.get("is_hidden", None)
        if not isinstance(is_hidden, bool):
            continue
        pokemon_and_hidden.append((name, is_hidden))
    
    return pokemon_and_hidden

def parse_localized_names(names: list[dict]) -> dict[str, str]:
    language_name_map = {}
    for entry in names:
        language = get_safe_from_path(entry, ["language", "name"])
        if not isinstance(language, str) or language not in NAMES_LANGUAGES:
            continue
        name = entry.get("name", None)
        if not isinstance(name, str):
            continue
        language_name_map[language] = name
    return language_name_map