import discord
import random
from typing import Optional
from src.apis.pokemon_api import PokemonApi
from src.constants.emoji_index import EmojiIndex
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.utils.dict_operations import get_safe_from_path
from src.utils.pokemon_operations import parse_localized_flavor_texts, parse_localized_names
from src.utils.string_operations import last_integer_from_url, format_name

POKEMON_API = PokemonApi.get_instance()
EMOJI_INDEX = EmojiIndex.get_instance()

NAMES_LANGUAGES = ["en", "de", "fr", "ja", "it", "es"]
FLAVORTEXT_LANGUAGES = ["en", "de", "fr"]

class PokemonMove(AbstractDatabaseEntity):
    TABLE_NAME = "pokemon_moves"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "move_id", "accuracy", "damage_class", "power", "pp", "type", "priority", "localized_names", "localized_flavor_texts", "effect", "short_effect", "effect_chance", "generation", "ailment", "ailment_chance", "category", "crit_rate", "drain", "flinch_chance", "healing", "min_hits", "max_hits", "min_turns", "max_turns", "stat_chance", "target"]
    SAVED_PROPERTIES = ["created_stamp", "move_id", "accuracy", "damage_class", "power", "pp", "type", "priority", "localized_names", "localized_flavor_texts", "effect", "short_effect", "effect_chance", "generation", "ailment", "ailment_chance", "category", "crit_rate", "drain", "flinch_chance", "healing", "min_hits", "max_hits", "min_turns", "max_turns", "stat_chance", "target"]

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
            localized_flavor_texts: Optional[dict[str, dict[str, str]]] = None,
            effect: Optional[str] = None,
            short_effect: Optional[str] = None,
            effect_chance: Optional[int] = None,
            generation: Optional[int] = None,
            ailment: Optional[str] = None,
            ailment_chance: Optional[int] = None,
            category: Optional[str] = None,
            crit_rate: Optional[int] = None,
            drain: Optional[int] = None,
            flinch_chance: Optional[int] = None,
            healing: Optional[int] = None,
            min_hits: Optional[int] = None,
            max_hits : Optional[int] = None,
            min_turns: Optional[int] = None,
            max_turns: Optional[int] = None,
            stat_chance: Optional[int] = None,
            target: Optional[str] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        self.move_id = move_id if isinstance(move_id, str) else "no-id"
        self.accuracy = accuracy if isinstance(accuracy, int) else 100
        self.damage_class = damage_class if isinstance(damage_class, str) else "unknown"
        self.power = power if isinstance(power, int) else 0
        self.pp = pp if isinstance(pp, int) else -1
        self.type = type if isinstance(type, str) else "unknown"
        self.priority = priority if isinstance(priority, int) else None
        self.localized_names = localized_names if isinstance(localized_names, dict) else {}
        self.localized_flavor_texts = localized_flavor_texts if isinstance(localized_flavor_texts, dict) else {}
        self.effect = effect if isinstance(effect, str) else "unknown effect"
        self.short_effect = short_effect if isinstance(short_effect, str) else "unknown effect"
        self.effect_chance = effect_chance if isinstance(effect_chance, int) else 100
        self.generation = generation if isinstance(generation, int) else -1
        self.ailment = ailment if isinstance(ailment, str) else "none"
        self.ailment_chance = ailment_chance if isinstance(ailment_chance, int) else 0
        self.category = category if isinstance(category, str) else "unknown"
        self.crit_rate = crit_rate if isinstance(crit_rate, int) else 0
        self.drain = drain if isinstance(drain, int) else 0
        self.flinch_chance = flinch_chance if isinstance(flinch_chance, int) else 0
        self.healing = healing if isinstance(healing, int) else 0
        self.min_hits = min_hits if isinstance(min_hits, int) else 0
        self.max_hits = max_hits if isinstance(max_hits, int) else 0
        self.min_turns = min_turns if isinstance(min_turns, int) else 0
        self.max_turns = max_turns if isinstance(max_turns, int) else 0
        self.stat_chance = stat_chance if isinstance(stat_chance, int) else 0
        self.target = target if isinstance(target, str) else "unknown"

        # If the effect is noteworthy over the existing short effect
        self.effect_important = self.is_effect_important()

    @staticmethod
    def from_api_data(data: dict) -> 'PokemonMove':
        move_id = data.get("name", None)
        accuracy = data.get("accuracy", None)
        damage_class = get_safe_from_path(data, ["damage_class", "name"])
        power = data.get("power", None)
        pp = data.get("pp", None)
        type = get_safe_from_path(data, ["type", "name"])
        priority = data.get("priority", None)
        effect_chance = data.get("effect_chance", None)
        target = get_safe_from_path(data, ["target", "name"])

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

        effect_entries = data.get("effect_entries", None)
        if not isinstance(effect_entries, list):
            effect = short_effect = None
        else:
            effect, short_effect = parse_effect_entries(entries=effect_entries)

        generation_url = get_safe_from_path(data, ["generation", "url"])
        if not isinstance(generation_url, str):
            generation = None
        else:
            generation = last_integer_from_url(url=generation_url)

        meta_data = data.get("meta", None)
        if isinstance(meta_data, dict):
            ailment = get_safe_from_path(meta_data, ["ailment", "name"])
            ailment_chance = meta_data.get("ailment_chance", None)
            category = get_safe_from_path(meta_data, ["category", "name"])
            crit_rate = meta_data.get("crit_rate", None)
            drain = meta_data.get("drain", None)
            flinch_chance = meta_data.get("flinch_chance", None)
            healing = meta_data.get("healing", None)
            min_hits = meta_data.get("min_hits", None)
            max_hits = meta_data.get("max_hits", None)
            min_turns = meta_data.get("min_turns", None)
            max_turns = meta_data.get("max_turns", None)
            stat_chance = meta_data.get("stat_chance", None)
        else:
            ailment = ailment_chance = category = crit_rate = drain = flinch_chance = healing = min_hits = max_hits = min_turns = max_turns = stat_chance = None

        return PokemonMove(
            move_id=move_id,
            accuracy=accuracy,
            damage_class=damage_class,
            power=power,
            pp=pp,
            type=type,
            priority=priority,
            localized_names=localized_names,
            localized_flavor_texts=localized_flavor_texts,
            effect=effect,
            short_effect=short_effect,
            effect_chance=effect_chance,
            generation=generation,
            ailment=ailment,
            ailment_chance=ailment_chance,
            category=category,
            crit_rate=crit_rate,
            drain=drain,
            flinch_chance=flinch_chance,
            healing=healing,
            min_hits=min_hits,
            max_hits=max_hits,
            min_turns=min_turns,
            max_turns=max_turns,
            stat_chance=stat_chance,
            target=target
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
            f"JA: **`{self.localized_names.get('ja', 'no japanese name')}`**",
            f"IT: **`{self.localized_names.get('it', 'no italian name')}`**",
            f"ES: **`{self.localized_names.get('es', 'no spanish name')}`**"
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
            
    def is_effect_important(self) -> bool:
        if len(self.effect) >= 2 * len(self.short_effect):
            return True
        
        keywords = ["note", "such as", "example"]
        lower_effect = self.effect.lower()
        for keyword in keywords:
            if keyword in lower_effect:
                return True
        
        return False
            
    def get_extra_info(self) -> str:
        extras = []

        if self.min_hits != 0 and self.max_hits != 0:
            extras.append(f"Hits {self.min_hits} to {self.max_hits} times")
        elif self.min_hits != 0:
            extras.append(f"Hits a minimum of {self.min_hits} times")
        elif self.max_hits != 0:
            extras.append(f"Hits a maximum of {self.max_hits} times")
        
        if self.min_turns != 0 and self.max_turns != 0:
            extras.append(f"Lasts {self.min_turns} to {self.max_turns} turns")
        elif self.min_turns != 0:
            extras.append(f"Lasts a minimum of {self.min_turns} turns")
        elif self.max_turns != 0:
            extras.append(f"Lasts a maximum of {self.max_turns} times")

        if self.drain > 0:
            extras.append(f"Heals {self.drain}% of damage dealt")
        elif self.drain < 0:
            extras.append(f"Damages user for {self.drain}% of damage dealt")

        if self.healing > 0:
            extras.append(f"Heals {self.healing}% of users max HP")

        if self.crit_rate > 0:
            extras.append(f"Crit rate bonus of {self.crit_rate}%")

        if self.ailment_chance > 0:
            extras.append(f"{self.ailment_chance}% chance of inflicting {format_name(self.ailment)}")

        if self.flinch_chance > 0:
            extras.append(f"{self.flinch_chance}% chance that target flinches")

        if self.stat_chance > 0:
            extras.append(f"{self.stat_chance}% chance to inflict stat change on target")

        return "\n".join([f"❥ `{extra}`" for extra in extras])
            
    def generate_general_embed(self) -> 'MoveEmbed':
        embed = MoveEmbed(
            move=self,
            title=f"{EMOJI_INDEX.get_emoji(self.type)} {self.get_name(language='en')} {EMOJI_INDEX.get_emoji(self.damage_class)}",
            description=f"*{self.get_random_flavor_text()}*"
        )
        embed.add_field(name="Names", value=self.get_different_localized_names())
        embed.add_field(name="Generation", value=f"**`{self.generation}`**")
        embed.add_field(name="Type", value=f"**`{self.type.capitalize()}`**")
        embed.add_field(name="Power", value=f"**`{self.power}`**")
        embed.add_field(name="Accuracy", value=f"**`{self.accuracy}`**")
        embed.add_field(name="PP", value=f"**`{self.pp}`**")
        embed.add_field(name="Damage Class", value=f"**`{self.damage_class.capitalize()}`**")
        embed.add_field(name="Category", value=f"**`{format_name(self.category)}`**")
        embed.add_field(name="Priority", value=f"**`{self.priority}`**")
        embed.add_field(name="Target", value=f"**`{format_name(self.target)}`**")
        embed.add_field(name="Effect Chance", value=f"**`{self.effect_chance}%`**")
        embed.add_field(name="Effect", value=f"**`{self.short_effect}`**", inline=False)

        extra_info = self.get_extra_info()
        if len(extra_info) > 0:
            embed.add_field(name="Meta Data", value=self.get_extra_info(), inline=False)
        return embed
    
    def generate_effect_embed(self) -> 'MoveEmbed':
        embed = MoveEmbed(
            move=self,
            title=f"Detailed Effects of {self.get_name(language='en')}",
            description=self.effect,
            disabled=not self.effect_important
        )
        return embed

class MoveEmbed(discord.Embed):
    def __init__(self, move: PokemonMove, disabled: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.move = move
        self.color = discord.Color.from_str("#78AEE3")
        self.disabled = disabled

    def timeout(self) -> None:
        self.color = discord.Color.dark_grey()
        self.set_footer(text="This interaction has timed out.")
            
def parse_effect_entries(entries: list[dict], language: str = "en") -> tuple[str, str]:
    language_effect_map = {}
    for entry in entries:
        effect = entry.get("effect", "unknown effect")
        short_effect = entry.get("short_effect", "unknown effect")
        effect_language = get_safe_from_path(entry, ["language", "name"])
        language_effect_map[effect_language] = (effect, short_effect)
    return language_effect_map.get(language, "unknown effect")

def parse_stat_changes(stat_changes: list[dict]) -> dict[str, int]:
    changes = {}
    for change in stat_changes:
        stat = change.get("stat", None)
        amount = change.get("change", None)
        if not stat or not amount:
            continue
        change[stat] = amount
    return changes