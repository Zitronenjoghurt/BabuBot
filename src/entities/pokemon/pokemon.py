from typing import Optional
from src.apis.pokemon_api import PokemonApi
from src.constants.config import Config
from src.constants.pokemon_names import PokemonNames
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.utils.dict_operations import get_ensure_dict

CONFIG = Config.get_instance()
POKEMON_API = PokemonApi.get_instance()
POKEMON_NAMES = PokemonNames.get_instance()

class Pokemon(AbstractDatabaseEntity):
    TABLE_NAME = "pokemon"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "name", "pokedex_number", "hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "types"]
    SAVED_PROPERTIES = ["created_stamp", "name", "pokedex_number", "hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "types"]

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
            types: Optional[list[str]] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        self.name = name.lower() if isinstance(name, str) else "No Name"
        self.pokedex_number = pokedex_number if isinstance(pokedex_number, int) else 0
        self.hp = hp if isinstance(hp, int) else 0
        self.attack = attack if isinstance(attack, int) else 0
        self.defense = defense if isinstance(defense, int) else 0
        self.sp_attack = sp_attack if isinstance(sp_attack, int) else 0
        self.sp_defense = sp_defense if isinstance(sp_defense, int) else 0
        self.speed = speed if isinstance(speed, int) else 0
        self.types = types if isinstance(types, list) else []

    @staticmethod
    def from_api_data(data: dict) -> 'Pokemon':
        name = data.get("name", None)
        if not name:
            raise RuntimeError(f"Tried to instantiate Pokemon from api data but it did not include a name.")
        pokedex_number = data.get("id", None)

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

        return Pokemon(
            name=name,
            pokedex_number=pokedex_number,
            hp=hp,
            attack=attack,
            defense=defense,
            sp_attack=sp_attack,
            sp_defense=sp_defense,
            speed=speed,
            types=types
        )
    
    @staticmethod
    async def fetch(pokemon_name: str) -> Optional['Pokemon']:
        name = POKEMON_NAMES.match_name(name=pokemon_name)
        if not name:
            return
        name = name.lower()

        pokemon = await Pokemon.find(name=name)
        if isinstance(pokemon, Pokemon):
            return pokemon
        
        data = await POKEMON_API.get_pokemon_data(name=name)
        if not data:
            return
        
        pokemon = Pokemon.from_api_data(data=data)
        await pokemon.save()
        return pokemon
    
    def get_image_url(self) -> str:
        return f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{self.pokedex_number}.png"