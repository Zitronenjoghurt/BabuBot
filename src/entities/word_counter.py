from typing import Optional
from src.constants.config import Config
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.utils.validator import validate_of_type

CONFIG = Config.get_instance()

class WordCounter(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["words"]

    def __init__(self, words: Optional[dict[str, int]] = None) -> None:
        if words is None:
            words = {}
        validate_of_type(words, dict, "words")

        self.words = words

    def count_word(self, word: str) -> None:
        if word not in self.words:
            self.words[word] = 0
        self.words[word] += 1