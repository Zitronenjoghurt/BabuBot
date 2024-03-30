from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.pokemon.gender import PokemonGender
from src.utils.dict_operations import get_safe_from_path

class EvolutionDetails(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["trigger", "item", "gender", "held_item", "known_move", "known_move_type", "location", "min_level", "min_happiness", "min_beauty", "min_affection", "needs_overworld_rain", "party_species", "party_type", "relative_physical_stats", "time_of_day", "trade_species", "turn_upside_down"]

    def __init__(
            self,
            trigger: Optional[str] = None,
            item: Optional[str] = None,
            gender: Optional[int] = None,
            held_item: Optional[str] = None,
            known_move: Optional[str] = None,
            known_move_type: Optional[str] = None,
            location: Optional[str] = None,
            min_level: Optional[int] = None,
            min_happiness: Optional[int] = None,
            min_beauty: Optional[int] = None,
            min_affection: Optional[int] = None,
            needs_overworld_rain: Optional[bool] = None,
            party_species: Optional[str] = None,
            party_type: Optional[str] = None,
            relative_physical_stats: Optional[int] = None,
            time_of_day: Optional[str] = None,
            trade_species: Optional[str] = None,
            turn_upside_down: Optional[bool] = None
        ) -> None:
        self.trigger = trigger if isinstance(trigger, str) else None
        self.item = item if isinstance(item, str) else None
        self.gender = gender if isinstance(gender, int) else None
        self.held_item = held_item if isinstance(held_item, str) else None
        self.known_move = known_move if isinstance(known_move, str) else None
        self.known_move_type = known_move_type if isinstance(known_move_type, str) else None
        self.location = location if isinstance(location, str) else None
        self.min_level = min_level if isinstance(min_level, int) else None
        self.min_happiness = min_happiness if isinstance(min_happiness, int) else None
        self.min_beauty = min_beauty if isinstance(min_beauty, int) else None
        self.min_affection = min_affection if isinstance(min_affection, int) else None
        self.needs_overworld_rain = needs_overworld_rain if isinstance(needs_overworld_rain, bool) else None
        self.party_species = party_species if isinstance(party_species, str) else None
        self.party_type = party_type if isinstance(party_type, str) else None
        self.relative_physical_stats = relative_physical_stats if isinstance(relative_physical_stats, int) else None
        self.time_of_day = time_of_day if isinstance(time_of_day, str) else None
        self.trade_species = trade_species if isinstance(trade_species, str) else None
        self.turn_upside_down = turn_upside_down if isinstance(turn_upside_down, bool) else None

        self.gender_type = PokemonGender(gender) if isinstance(gender, int) else None

    @staticmethod
    def from_api_data(data: dict) -> 'EvolutionDetails':
        trigger = get_safe_from_path(data, ["trigger", "name"])
        item = get_safe_from_path(data, ["item", "name"])
        gender = data.get("gender", None)
        held_item = get_safe_from_path(data, ["held_item", "name"])
        known_move = get_safe_from_path(data, ["known_move", "name"])
        known_move_type = get_safe_from_path(data, ["known_move_type", "name"])
        location = get_safe_from_path(data, ["location", "name"])
        min_level = data.get("min_level", None)
        min_happiness = data.get("min_happiness", None)
        min_beauty = data.get("min_beauty", None)
        min_affection = data.get("min_affection", None)
        needs_overworld_rain = data.get("needs_overworld_rain", None)
        party_species = get_safe_from_path(data, ["party_species", "name"])
        party_type = get_safe_from_path(data, ["party_type", "name"])
        relative_physical_stats = data.get("relative_physical_stats", None)
        time_of_day = data.get("time_of_day", None)
        trade_species = get_safe_from_path(data, ["trade_species", "name"])
        turn_upside_down = data.get("turn_upside_down", None)

        return EvolutionDetails(
            trigger=trigger,
            item=item,
            gender=gender,
            held_item=held_item,
            known_move=known_move,
            known_move_type=known_move_type,
            location=location,
            min_level=min_level,
            min_happiness=min_happiness,
            min_beauty=min_beauty,
            min_affection=min_affection,
            needs_overworld_rain=needs_overworld_rain,
            party_species=party_species,
            party_type=party_type,
            relative_physical_stats=relative_physical_stats,
            time_of_day=time_of_day,
            trade_species=trade_species,
            turn_upside_down=turn_upside_down
        )