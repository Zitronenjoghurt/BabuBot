from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.utils.dict_operations import get_safe_from_path
from src.utils.string_operations import format_name

class Move(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["id", "name", "level_learned_at", "learn_methods"]

    def __init__(
            self, 
            id: Optional[str] = None, 
            name: Optional[str] = None, 
            level_learned_at: Optional[int] = None, 
            learn_methods: Optional[list[str]] = None
        ) -> None:
        self.id = id if isinstance(id, str) else "no-id"
        self.name = name if isinstance(name, str) else "No Name"
        self.level_learned_at = level_learned_at if isinstance(level_learned_at, int) else 0
        self.learn_methods = learn_methods if isinstance(learn_methods, list) else []

class VersionMoves(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["moves"]
    SERIALIZE_CLASSES = {"moves": Move}
    NESTED_DICT_PROPERTIES = ["moves"]

    def __init__(self, moves: Optional[dict[str, Move]] = None) -> None:
        self.moves = moves if isinstance(moves, dict) else {}

    def add_move(self, move: Move) -> None:
        if not isinstance(move, Move):
            return
        self.moves[move.id] = move

    def has_move(self, id: str) -> bool:
        return id in self.moves

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
                
                if moves_by_version[version_name].has_move(move_id):
                    if level_learned_at > 0:
                        moves_by_version[version_name].moves[move_id].level_learned_at = level_learned_at
                    moves_by_version[version_name].moves[move_id].learn_methods.append(learn_method)
                else:
                    move = Move(id=move_id, name=format_name(move_id), level_learned_at=level_learned_at, learn_methods=[learn_method])
                    moves_by_version[version_name].add_move(move=move)
        
        return LearningMoves(
            moves_by_version=moves_by_version
        )