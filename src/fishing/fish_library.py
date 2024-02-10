from src.fishing.fish_entry import FishEntry
from src.utils.file_operations import construct_path, file_to_dict

DATA_FILE_PATH = construct_path("src/data/fish.json")

class FishLibrary():
    _instance = None

    def __init__(self) -> None:
        if FishLibrary._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of FishLibrary.")
        self.fish = {}
        self._initialize_entries()

    def _initialize_entries(self) -> None:
        fish_data = file_to_dict(DATA_FILE_PATH)
        for id, data in fish_data.items():
            data["id"] = id
            entry = FishEntry.from_dict(data=data)
            self.fish[id] = entry

    @staticmethod
    def get_instance() -> 'FishLibrary':
        if FishLibrary._instance is None:
            FishLibrary._instance = FishLibrary()
        return FishLibrary._instance