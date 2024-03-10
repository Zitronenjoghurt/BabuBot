from typing import Optional
from src.apis.pokemon_api import PokemonApi
from src.constants.config import Config
from src.constants.pokemon_names import PokemonNames
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.pokemon.evolution_chain import EvolutionChain
from src.utils.dict_operations import get_ensure_dict, get_safe_from_path
from src.utils.string_operations import last_integer_from_url

CONFIG = Config.get_instance()
POKEMON_API = PokemonApi.get_instance()
POKEMON_NAMES = PokemonNames.get_instance()

NAMES_LANGUAGES = ["en", "de", "fr", "ja", "roomaji"]
FLAVORTEXT_LANGUAGES = ["en", "de", "fr"]

class Pokemon(AbstractDatabaseEntity):
    TABLE_NAME = "pokemon"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "name", "pokedex_number", "hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "types", "chain_id", "capture_rate", "is_baby", "is_legendary", "is_mythical", "localized_names", "localized_flavor_texts", "generation", "growth_rate", "height", "weight"]
    SAVED_PROPERTIES = ["created_stamp", "name", "pokedex_number", "hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "types", "chain_id", "capture_rate", "is_baby", "is_legendary", "is_mythical", "localized_names", "localized_flavor_texts", "generation", "growth_rate", "height", "weight"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            name: Optional[str] = None,
            pokedex_number: Optional[int] = None,
            hp: Optional[int] = None,
            attack: Optional[int] = None,
            defense: Optional[int] = None,
            sp_attack: Optional[int] = None,
            sp_defense: Optional[int] = None,
            speed: Optional[int] = None,
            types: Optional[list[str]] = None,
            chain_id: Optional[int] = None,
            capture_rate: Optional[int] = None,
            is_baby: Optional[bool] = None,
            is_legendary: Optional[bool] = None,
            is_mythical: Optional[bool] = None,
            localized_names: Optional[dict[str, str]] = None,
            localized_flavor_texts: Optional[dict[str, dict[str, str]]] = None,
            generation: Optional[int] = None,
            growth_rate: Optional[str] = None,
            height: Optional[int] = None, # height in decimeter
            weight: Optional[int] = None  # weight in hectograms
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        self.name = name.lower() if isinstance(name, str) else "Missing Name"
        self.pokedex_number = pokedex_number if isinstance(pokedex_number, int) else 0
        self.hp = hp if isinstance(hp, int) else 0
        self.attack = attack if isinstance(attack, int) else 0
        self.defense = defense if isinstance(defense, int) else 0
        self.sp_attack = sp_attack if isinstance(sp_attack, int) else 0
        self.sp_defense = sp_defense if isinstance(sp_defense, int) else 0
        self.speed = speed if isinstance(speed, int) else 0
        self.types = types if isinstance(types, list) else []
        self.chain_id = chain_id if isinstance(chain_id, int) else None
        self.capture_rate = capture_rate if isinstance(capture_rate, int) else -1
        self.is_baby = is_baby if isinstance(is_baby, bool) else False
        self.is_legendary = is_legendary if isinstance(is_legendary, bool) else False
        self.is_mythical = is_mythical if isinstance(is_mythical, bool) else False
        self.localized_names = localized_names if isinstance(localized_names, dict) else {}
        self.localized_flavor_texts = localized_flavor_texts if isinstance(localized_flavor_texts, dict) else {}
        self.generation = generation if isinstance(generation, int) else -1
        self.growth_rate = growth_rate if isinstance(growth_rate, str) else None
        self.height = height if isinstance(height, int) else 0
        self.weight = weight if isinstance(weight, int) else 0

        self.evolution_chain: Optional[EvolutionChain] = None

    @staticmethod
    async def from_api_data(data: dict) -> 'Pokemon':
        name = data.get("name", None)
        if not name:
            raise RuntimeError(f"Tried to instantiate Pokemon from api data but it did not include a name.")
        pokedex_number = data.get("id", None)
        height = data.get("height", None)
        weight = data.get("weight", None)

        stats = data.get("stats", None)
        if len(stats) == 6:
            hp_data, attack_data, defense_data, sp_attack_data, sp_defense_data, speed_data = stats
            hp = hp_data.get("base_stat")
            attack = attack_data.get("base_stat")
            defense = defense_data.get("base_stat")
            sp_attack = sp_attack_data.get("base_stat")
            sp_defense = sp_defense_data.get("base_stat")
            speed = speed_data.get("base_stat")
        else:
            hp, attack, defense, sp_attack, sp_defense, speed = None, None, None, None, None, None

        types_data = data.get("types", [])
        types = []
        for type_data in types_data:
            type_data_specific = get_ensure_dict(type_data, "type")
            type_name = type_data_specific.get("name", None)
            if isinstance(type_name, str):
                types.append(type_name)

        evolution_chain_url = data.get("evolution_chain_url", None)
        if not evolution_chain_url:
            chain_id = None
        else:
            chain_id = last_integer_from_url(url=evolution_chain_url)

        species_data = data.get("species", None)
        if not species_data:
            capture_rate, is_baby, is_legendary, is_mythical, localized_names, localized_flavor_texts, generation, growth_rate = None, None, None, None, None, None, None, None
        else:
            capture_rate = species_data.get("capture_rate", None)
            is_baby = species_data.get("is_baby", None)
            is_legendary = species_data.get("is_legendary", None)
            is_mythical = species_data.get("is_mythical", None)
            growth_rate = get_safe_from_path(species_data, ["growth_rate", "name"])

            names = species_data.get("names", None)
            if not isinstance(names, list):
                localized_names = None
            else:
                localized_names = parse_localized_names(names=names)

            flavor_text_entries = species_data.get("flavor_text_entries", None)
            if not isinstance(flavor_text_entries, list):
                localized_flavor_texts = None
            else:
                localized_flavor_texts = parse_localized_flavor_texts(texts=flavor_text_entries)

            generation_url = get_safe_from_path(species_data, ["generation", "url"])
            if not isinstance(generation_url, str):
                generation = None
            else:
                generation = last_integer_from_url(url=generation_url)
                
        return Pokemon(
            name=name,
            pokedex_number=pokedex_number,
            hp=hp,
            attack=attack,
            defense=defense,
            sp_attack=sp_attack,
            sp_defense=sp_defense,
            speed=speed,
            types=types,
            chain_id=chain_id,
            capture_rate=capture_rate,
            is_baby=is_baby,
            is_legendary=is_legendary,
            is_mythical=is_mythical,
            localized_names=localized_names,
            localized_flavor_texts=localized_flavor_texts,
            generation=generation,
            growth_rate=growth_rate,
            height=height,
            weight=weight
        )
    
    @staticmethod
    async def fetch(pokemon_name: str) -> Optional['Pokemon']:
        name = POKEMON_NAMES.match_name(name=pokemon_name)
        if not name:
            return
        name = name.lower()

        pokemon = await Pokemon.find(name=name)
        if not isinstance(pokemon, Pokemon):
            data = await POKEMON_API.get_pokemon_data(name=name)
            if not data:
                return
            
            pokemon = await Pokemon.from_api_data(data=data)
            await pokemon.save()
        
        if pokemon.chain_id:
            pokemon.evolution_chain = await EvolutionChain.fetch(chain_id=pokemon.chain_id)
        return pokemon
    
    def get_image_url(self) -> str:
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{self.pokedex_number}.png"
    
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

def parse_localized_flavor_texts(texts: list[dict]) -> dict[str, dict[str, str]]:
    version_language_text_map = {}
    for entry in texts:
        language = get_safe_from_path(entry, ["language", "name"])
        if not isinstance(language, str) or language not in FLAVORTEXT_LANGUAGES:
            continue
        version = get_safe_from_path(entry, ["version", "name"])
        if not isinstance(version, str):
            continue
        text = entry.get("flavor_text", None)
        if not isinstance(text, str):
            continue
        if version not in version_language_text_map:
            version_language_text_map[version] = {}
        version_language_text_map[version][language] = text.replace("\n", " ")
    return version_language_text_map