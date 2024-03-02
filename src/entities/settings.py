from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

LABELS = {
    "ai_responses": "The bot can use your messages for ai generated responses (they will not be used for training)"
}

def yesno(state: bool): 
    if state:
        return "YES"
    return "NO"

class Settings(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["ai_responses"]

    def __init__(
            self, 
            ai_responses: Optional[bool] = None
        ) -> None:
        if ai_responses is None:
            ai_responses = True

        self.ai_responses = ai_responses

    # Returns true when a setting was updated
    def update(self, ai_responses: Optional[bool] = None) -> bool:
        updated = False
        if isinstance(ai_responses, bool):
            updated = True
            self.ai_responses = ai_responses
        return updated
    
    def get_fields(self) -> list[tuple[str, str]]:
        fields = []
        for key, label in LABELS.items():
            state = yesno(getattr(self, key))
            fields.append((label, f"**`{state}`**"))
        return fields