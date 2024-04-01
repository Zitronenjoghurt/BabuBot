import random
from typing import Optional
from src.apis.pokemon_api import PokemonApi
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.utils.dict_operations import get_safe_from_path
from src.utils.pokemon_operations import parse_localized_flavor_texts, parse_localized_names
from src.utils.string_operations import format_name

POKEMON_API = PokemonApi.get_instance()

NAMES_LANGUAGES = ["en", "de", "fr", "ja"]
FLAVORTEXT_LANGUAGES = ["en", "de", "fr"]

class PokemonMove(AbstractDatabaseEntity):
    TABLE_NAME = "pokemon_moves"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "move_id", "accuracy", "damage_class", "power", "pp", "type", "priority", "localized_names", "localized_flavor_texts"]
    SAVED_PROPERTIES = ["created_stamp", "move_id", "accuracy", "damage_class", "power", "pp", "type", "priority", "localized_names", "localized_flavor_texts"]

    def __init__(
            self,
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            move_id: Optional[str] = None,
            accuracy: Optional[int] = None,
            damage_class: Optional[str] = None,
            power: Optional[int] = None,
            pp: Optional[int] = None,
            type: Optional[str] = None,
            priority: Optional[int] = None,
            localized_names: Optional[dict[str, str]] = None,
            localized_flavor_texts: Optional[dict[str, dict[str, str]]] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        self.move_id = move_id if isinstance(move_id, str) else "no-id"
        self.accuracy = accuracy if isinstance(accuracy, int) else -1
        self.damage_class = damage_class if isinstance(damage_class, str) else "unknown"
        self.power = power if isinstance(power, int) else 0
        self.pp = pp if isinstance(pp, int) else -1
        self.type = type if isinstance(type, str) else "unknown"
        self.priority = priority if isinstance(priority, int) else None
        self.localized_names = localized_names if isinstance(localized_names, dict) else {}
        self.localized_flavor_texts = localized_flavor_texts if isinstance(localized_flavor_texts, dict) else {}

    @staticmethod
    def from_api_data(data: dict) -> 'PokemonMove':
        move_id = data.get("name", None)
        accuracy = data.get("accuracy", None)
        damage_class = get_safe_from_path(data, ["damage_class", "name"])
        power = data.get("power", None)
        pp = data.get("pp", None)
        type = get_safe_from_path(data, ["type", "name"])
        priority = data.get("priority", None)

        names = data.get("names", None)
        if not isinstance(names, list):
            localized_names = None
        else:
            localized_names = parse_localized_names(names=names, languages=NAMES_LANGUAGES)

        flavor_text_entries = data.get("flavor_text_entries", None)
        if not isinstance(flavor_text_entries, list):
            localized_flavor_texts = None
        else:
            localized_flavor_texts = parse_localized_flavor_texts(texts=flavor_text_entries, languages=FLAVORTEXT_LANGUAGES)

        return PokemonMove(
            move_id=move_id,
            accuracy=accuracy,
            damage_class=damage_class,
            power=power,
            pp=pp,
            type=type,
            priority=priority,
            localized_names=localized_names,
            localized_flavor_texts=localized_flavor_texts
        )
    
    @staticmethod
    async def fetch(move_id: str) -> Optional['PokemonMove']:
        move = await PokemonMove.find(move_id=move_id)
        if isinstance(move, PokemonMove):
            return move
        
        move_data = await POKEMON_API.get_move_data(name=move_id)
        if not isinstance(move_data, dict):
            return None
        
        move = PokemonMove.from_api_data(data=move_data)
        await move.save()
        return move
    
    def get_name(self, language: str) -> str:
        return self.localized_names.get(language, "Missing Name")
    
    def get_random_flavor_text(self) -> str:
        versions = list(self.localized_flavor_texts.keys())
        if not isinstance(versions, list) or len(versions) == 0:
            return "Missing Flavor Text"
        
        random_version_index = random.randint(0, len(versions) - 1)
        random_version = versions[random_version_index]
        text = get_safe_from_path(self.localized_flavor_texts, [random_version, "en"])
        if not isinstance(text, str):
            return "Missing English Flavor Text"
        
        return text
    
    def get_different_localized_names(self) -> str:
        names = [
            f"DE: **`{self.localized_names.get('de', 'no german name')}`**",
            f"FR: **`{self.localized_names.get('fr', 'no french name')}`**",
            f"JA: **`{self.localized_names.get('ja', 'no japanese name')}`**"
        ]
        return "\n".join(names)
    
    def get_damage_class_abbreviation(self) -> str:
        match self.damage_class:
            case "physical":
                return "PHY"
            case "special":
                return "SP"
            case "status":
                return "STAT"
            case _:
                return "NaN"