from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.pokemon.gender import PokemonGender
from src.utils.dict_operations import get_safe_from_path
from src.utils.string_operations import format_name

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
    
    def to_string(self) -> Optional[str]:
        if not isinstance(self.trigger, str):
            return
        
        string = f"On: **`{format_name(self.trigger)}`**"
        extra = []

        if isinstance(self.item, str):
            extra.append(f"Use item: **`{format_name(self.item)}`**")
        if isinstance(self.gender_type, PokemonGender):
            extra.append(f"Gender: **`{self.gender_type.name}`**")
        if isinstance(self.held_item, str):
            extra.append(f"Hold item: **`{format_name(self.held_item)}`**")
        if isinstance(self.known_move, str):
            extra.append(f"Know move: **`{format_name(self.known_move)}`**")
        if isinstance(self.known_move_type, str):
            extra.append(f"Know move of type: **`{self.known_move_type}`**")
        if isinstance(self.location, str):
            extra.append(f"At location: **`{format_name(self.location)}`**")
        if isinstance(self.min_level, int):
            extra.append(f"At level: **`{str(self.min_level)}`**")
        if isinstance(self.min_happiness, int):
            extra.append(f"Min happiness: **`{str(self.min_happiness)}`**")
        if isinstance(self.min_beauty, int):
            extra.append(f"Min beauty: **`{str(self.min_beauty)}`**")
        if isinstance(self.min_affection, int):
            extra.append(f"Min affection: **`{str(self.min_affection)}`**")
        if isinstance(self.needs_overworld_rain, bool) and self.needs_overworld_rain is True:
            extra.append(f"**`While its raining`**")
        if isinstance(self.party_species, str):
            extra.append(f"Pokemon in party: **`{format_name(self.party_species)}`**")
        if isinstance(self.party_type, str):
            extra.append(f"Pokemon of type in party: **`{self.party_type}`**")
        if isinstance(self.relative_physical_stats, int):
            match self.relative_physical_stats:
                case -1:
                    stats = "atk > def"
                case 0:
                    stats = "atk = def"
                case 1:
                    stats = "atk < def"
                case _:
                    stats = "UNKNOWN"
            extra.append(f"Relative physical stats: **`{stats}`**")
        if isinstance(self.time_of_day, str) and len(self.time_of_day) > 0:
            extra.append(f"At time of day: **`{self.time_of_day}`**")
        if isinstance(self.trade_species, str):
            extra.append(f"Traded for: **`{format_name(self.trade_species)}`**")
        if isinstance(self.turn_upside_down, bool) and self.turn_upside_down is True:
            extra.append(f"**`While device is turned upside down`**")

        if extra:
            extra_string = "\n".join(extra)
            string += f"\n{extra_string}"
        else:
            return

        return string