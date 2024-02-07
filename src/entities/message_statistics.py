from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.utils.validator import validate_of_type

class MessageStatistics(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["message_count", "total_characters"]

    def __init__(
            self, 
            message_count: Optional[int] = None,
            total_characters: Optional[int] = None
        ) -> None:
        if message_count is None:
            message_count = 0
        if total_characters is None:
            total_characters = 0

        self.message_count = message_count
        self.total_characters = total_characters

    @staticmethod
    def accumulate(message_statistics_entities: list['MessageStatistics']) -> 'MessageStatistics':
        message_count = 0
        total_characters = 0
        for message_statistics in message_statistics_entities:
            message_count += message_statistics.message_count
            total_characters += message_statistics.total_characters
        return MessageStatistics(message_count=message_count, total_characters=total_characters)

    def process_message(self, message: str) -> None:
        validate_of_type(message, str, "message")
        self.message_count += 1
        self.total_characters += len(message)