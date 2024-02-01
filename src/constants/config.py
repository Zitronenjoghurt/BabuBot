from src.utils.file_operations import construct_path, file_to_dict
from src.utils.validator import validate_of_type

CONFIG_FILE_PATH = construct_path("src/config.json")

class Config():
    _instance = None

    def __init__(self) -> None:
        if Config._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of Config.")
        
        config_data = file_to_dict(CONFIG_FILE_PATH)
        
        self.BOT_TOKEN = config_data.get("token", None)

        try:
            validate_of_type(self.BOT_TOKEN, str, "token")
        except ValueError as e:
            raise RuntimeError(f"An error occured while initializing config: {e}")

    @staticmethod
    def get_instance() -> 'Config':
        if Config._instance is None:
            Config._instance = Config()
        return Config._instance