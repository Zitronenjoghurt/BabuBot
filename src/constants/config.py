from src.utils.file_operations import construct_path, file_to_dict
from src.logging.logger import LOGGER
from src.utils.validator import validate_of_type, validate_all_in_of_type

CONFIG_FILE_PATH = construct_path("src/config.json")

class Config():
    _instance = None

    def __init__(self) -> None:
        if Config._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of Config.")
        
        config_data = file_to_dict(CONFIG_FILE_PATH)
        
        self.BOT_TOKEN = config_data.get("token", None)
        self.NASA_API_KEY = config_data.get("nasa_key", "")
        self.CAT_API_KEY = config_data.get("cat_key", "")
        self.YOUTUBE_API_KEY = config_data.get("youtube_key", "")
        self.OPENAI_API_KEY = config_data.get("openai_key", "")
        self.PREFIX = config_data.get("prefix", None)
        self.GUILD_ID = config_data.get("guild_id", None)
        self.COUNTED_WORDS = config_data.get("counted_words", [])
        self.IGNORED_CHANNEL_IDS = config_data.get("ignored_channel_ids", [])
        # If the message event encounters this word, it will not process the message
        self.IGNORED_MESSAGE_WORDS = config_data.get("ignored_message_words", [])
        self.DECIMAL_DIGITS = config_data.get("decimal_digits", 2)
        self.CURRENCY = config_data.get("currency", "$")
        self.FISHING_CHANNEL_ID = config_data.get("fishing_channel_id", None)
        self.LOG_CHANNEL_ID = config_data.get("log_channel_id", None)
        self.YOUTUBE_NOTIFICATION_CHANNEL_ID = config_data.get("youtube_notification_channel_id", None)

        try:
            validate_of_type(self.BOT_TOKEN, str, "token")
            validate_of_type(self.NASA_API_KEY, str, "nasa_key")
            validate_of_type(self.CAT_API_KEY, str, "cat_key")
            validate_of_type(self.YOUTUBE_API_KEY, str, "youtube_key")
            validate_of_type(self.OPENAI_API_KEY, str, "openai_key")
            validate_of_type(self.PREFIX, str, "prefix")
            validate_of_type(self.GUILD_ID, int, "guild_id")
            validate_of_type(self.COUNTED_WORDS, list, "counted_words")
            validate_all_in_of_type(self.COUNTED_WORDS, str, "word", "counted_words")
            validate_of_type(self.IGNORED_CHANNEL_IDS, list, "ignored_channel_ids")
            validate_all_in_of_type(self.IGNORED_CHANNEL_IDS, int, "channel_id", "ignored_channel_ids")
            validate_of_type(self.IGNORED_MESSAGE_WORDS, list, "ignored_message_words")
            validate_all_in_of_type(self.IGNORED_MESSAGE_WORDS, str, "word", "ignored_message_words")
            validate_of_type(self.DECIMAL_DIGITS, int, "decimal_digits")
            validate_of_type(self.CURRENCY, str, "currency")
            validate_of_type(self.FISHING_CHANNEL_ID, int, "fishing_channel_id")
            validate_of_type(self.LOG_CHANNEL_ID, int, "log_channel_id")
            validate_of_type(self.YOUTUBE_NOTIFICATION_CHANNEL_ID, int, "youtube_notification_channel_id")
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