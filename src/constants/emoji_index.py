from src.utils.file_operations import construct_path, file_to_dict

EMOJI_FILE_PATH = construct_path("src/data/emojis.json")

class EmojiIndex():
    _instance = None

    def __init__(self) -> None:
        if EmojiIndex._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of EmojiIndex.")
        
        self.emojis = file_to_dict(EMOJI_FILE_PATH)

    @staticmethod
    def get_instance() -> 'EmojiIndex':
        if EmojiIndex._instance is None:
            EmojiIndex._instance = EmojiIndex()
        return EmojiIndex._instance
    
    def get_emoji(self, name: str) -> str:
        id = self.emojis.get(name, "UNKNOWN")
        return f"<:{name}:{id}>"