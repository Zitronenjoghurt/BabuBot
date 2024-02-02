from src.utils.file_operations import construct_path, file_to_dict
from src.utils.validator import validate_of_type, validate_all_in_of_type

CONFIG_FILE_PATH = construct_path("src/config.json")

class Config():
    _instance = None

    def __init__(self) -> None:
        if Config._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of Config.")
        
        config_data = file_to_dict(CONFIG_FILE_PATH)
        
        self.BOT_TOKEN = config_data.get("token", None)
        self.PREFIX = config_data.get("prefix", None)
        self.GUILD_ID = config_data.get("guild_id", None)
        self.COUNTED_WORDS = config_data.get("counted_words", [])
        self.IGNORED_CHANNEL_IDS = config_data.get("ignored_channel_ids", [])

        try:
            validate_of_type(self.BOT_TOKEN, str, "token")
            validate_of_type(self.PREFIX, str, "prefix")
            validate_of_type(self.GUILD_ID, int, "guild_id")
            validate_of_type(self.COUNTED_WORDS, list, "counted_words")
            validate_all_in_of_type(self.COUNTED_WORDS, str, "word", "counted_words")
            validate_of_type(self.IGNORED_CHANNEL_IDS, list, "ignored_channel_ids")
            validate_all_in_of_type(self.IGNORED_CHANNEL_IDS, int, "channel_id", "ignored_channel_ids")
        except ValueError as e:
            raise RuntimeError(f"An error occured while initializing config: {e}")

    @staticmethod
    def get_instance() -> 'Config':
        if Config._instance is None:
            Config._instance = Config()
        return Config._instance
    
    def countable_words_in_message(self, message: str) -> list[str]:
        message = message.lower()
        hits = []
        for word in self.COUNTED_WORDS:
            if word in message:
                hits.append(word)
        return hits