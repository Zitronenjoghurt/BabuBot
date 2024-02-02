from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity
from src.utils.dict_operations import sort_simple
from src.utils.validator import validate_of_type

class WordCounter(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["words"]

    def __init__(self, words: Optional[dict[str, int]] = None) -> None:
        if words is None:
            words = {}
        validate_of_type(words, dict, "words")

        self.words: dict[str, int] = sort_simple(words, descending=True)

    def __str__(self) -> str:
        return "\n".join([f"{word}: {count}" for word, count in self.words.items()])
    
    def to_string_with_positions(self, positions: dict[str, int]) -> str:
        word_strings = []
        for word, count in self.words.items():
            position = positions.get(word, "NaN")
            word_strings.append(f"**{word}**: `{count} | #{position}`")
        return "\n".join(word_strings)

    @staticmethod
    def accumulate(word_counters: list['WordCounter']) -> 'WordCounter':
        words = {}
        for word_counter in word_counters:
            for word, count in word_counter.words.items():
                if word not in words:
                    words[word] = 0
                words[word] += count
        return WordCounter(words=words)

    def count_word(self, word: str) -> None:
        if word not in self.words:
            self.words[word] = 0
        self.words[word] += 1