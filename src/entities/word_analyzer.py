from typing import Optional
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.word_counter import WordCounter

MIN_LENGTH = 1
MAX_LENGTH = 20

class WordAnalyzer(AbstractDatabaseEntity):
    TABLE_NAME = "word_analyzer"
    SERIALIZE_CLASSES = {"word_counter": WordCounter}
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "userid", "word_counter"]
    SAVED_PROPERTIES = ["created_stamp", "userid", "word_counter"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            userid: Optional[str] = None,
            word_counter: Optional[WordCounter] = None
        ) -> None:
        super().__init__(id, created_stamp)
        if userid is None:
            userid = ""
        if word_counter is None:
            word_counter = WordCounter()

        self.userid = str(userid)
        self.word_counter = word_counter

    def process_word(self, word: str) -> None:
        if not isinstance(word, str):
            return
        
        length = len(word)
        if word.isalpha() and length >= MIN_LENGTH and length <= MAX_LENGTH:
            self.word_counter.count_word(word=word)