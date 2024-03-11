from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.utils.dict_operations import get_safe_from_path

class LearningMoves(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["moves_by_version"]

    def __init__(
            self,
            moves_by_version: Optional[dict] = None
        ) -> None:
        self.moves_by_version = moves_by_version if isinstance(moves_by_version, dict) else {}

    @staticmethod
    def from_api_data(data: list) -> 'LearningMoves':
        moves_by_version = {} # {version: {move_name: {level_learned_at: 0, methods: []}}}

        for move_data in data:
            move_name = get_safe_from_path(move_data, ["move", "name"])
            if not isinstance(move_name, str):
                continue
            version_details = move_data.get("version_group_details", None)
            if not isinstance(version_details, list):
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
                    moves_by_version[version_name] = {}
                
                if move_name in moves_by_version[version_name]:
                    if level_learned_at > 0:
                        moves_by_version[version_name][move_name]["level"] = level_learned_at
                    moves_by_version[version_name][move_name]["methods"].append(learn_method)
                else:
                    moves_by_version[version_name][move_name] = {"level": level_learned_at, "methods": [learn_method]}
        


        return LearningMoves(
            moves_by_version=moves_by_version
        )