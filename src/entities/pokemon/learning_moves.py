from typing import Optional
from src.constants.emoji_index import EmojiIndex
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.entities.pokemon.move import PokemonMove
from src.utils.dict_operations import get_safe_from_path
from src.utils.string_operations import format_name

EMOJI_INDEX = EmojiIndex.get_instance()

class MoveInfo(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["id", "name", "level_learned_at", "learn_method"]

    def __init__(
            self, 
            id: Optional[str] = None, 
            name: Optional[str] = None, 
            level_learned_at: Optional[int] = None, 
            learn_method: Optional[str] = None
        ) -> None:
        self.id = id if isinstance(id, str) else "no-id"
        self.name = name if isinstance(name, str) else "No Name"
        self.level_learned_at = level_learned_at if isinstance(level_learned_at, int) else 0
        self.learn_method = learn_method if isinstance(learn_method, str) else "None"

    async def get_string(self) -> str:
        move = await PokemonMove.fetch(move_id=self.id)

        match self.learn_method:
            case "level-up":
                method_string = f"{self.level_learned_at}"
            case "egg":
                method_string = "EGG"
            case _:
                method_string = "NaN"
        if isinstance(move, PokemonMove):
            name = move.get_name(language="en")
            type = move.type
        else:
            name = "No Name"
            type = "unknown"

        return f"**`{method_string}`** ❥ {EMOJI_INDEX.get_emoji(name=type)} **{name}**"

class VersionMoves(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["moves"]
    SERIALIZE_CLASSES = {"moves": MoveInfo}
    NESTED_DICT_PROPERTIES = ["moves"]

    def __init__(self, moves: Optional[list[MoveInfo]] = None) -> None:
        self.moves = moves if isinstance(moves, list) else []

    def add_move(self, move: MoveInfo) -> None:
        self.moves.append(move)

    def has_move(self, id: str) -> bool:
        return id in self.moves
    
    async def get_move_strings(self, lvl_moves: bool = True, egg_moves: bool = False) -> list[str]:
        sorted_moves = sorted(self.moves, key=lambda move: move.level_learned_at)

        move_strings = []
        for move in sorted_moves:
            if not lvl_moves and move.learn_method == "level-up" or not egg_moves and move.learn_method == "egg":
                continue
            move_string = await move.get_string()
            move_strings.append(move_string)
        
        return move_strings

class LearningMoves(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["moves_by_version"]
    SERIALIZE_CLASSES = {"moves_by_version": VersionMoves}
    NESTED_DICT_PROPERTIES = ["moves_by_version"]

    def __init__(
            self,
            moves_by_version: Optional[dict[str, VersionMoves]] = None
        ) -> None:
        self.moves_by_version = moves_by_version if isinstance(moves_by_version, dict) else {}

    @staticmethod
    def from_api_data(data: list) -> 'LearningMoves':
        moves_by_version: dict[str, VersionMoves] = {}

        for move_data in data:
            move_id = get_safe_from_path(move_data, ["move", "name"])
            version_details = move_data.get("version_group_details", None)
            if not isinstance(move_id, str) or not isinstance(version_details, list):
                continue
            
            for version_detail in version_details:
                learn_method = get_safe_from_path(version_detail, ["move_learn_method", "name"])
                if not isinstance(learn_method, str) or learn_method in ["machine", "tutor"]: # skipping machines since its not needed as of rn
                    continue
                version_name = get_safe_from_path(version_detail, ["version_group", "name"])
                if not isinstance(version_name, str):
                    continue

                level_learned_at = version_detail.get("level_learned_at", 0)
                
                if version_name not in moves_by_version:
                    moves_by_version[version_name] = VersionMoves()

                move = MoveInfo(id=move_id, name=format_name(move_id), level_learned_at=level_learned_at, learn_method=learn_method)
                moves_by_version[version_name].add_move(move=move)
        
        return LearningMoves(
            moves_by_version=moves_by_version
        )
    
    async def get_moves_string(self, version: str, lvl_moves: bool = True, egg_moves: bool = False) -> Optional[str]:
        if version not in self.moves_by_version:
            return
        version_moves = self.moves_by_version[version]
        move_strings = await version_moves.get_move_strings(lvl_moves=lvl_moves, egg_moves=egg_moves)
        return "\n".join(move_strings)