from openai import OpenAI
from typing import Optional
from src.apis.abstract_api_controller import AbstractApiController
from src.apis.rate_limiting import rate_limit
from src.constants.config import Config
from src.logging.logger import LOGGER
from src.utils.file_operations import construct_path, file_to_dict

CONFIG = Config.get_instance()
PRESETS_FILE_PATH = construct_path("src/data/ai_presets/{name}.json")

class OpenAIApi(AbstractApiController):
    _instance = None
    CALLS = 5
    SECONDS = 20

    def __init__(self) -> None:
        if OpenAIApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of OpenAIApi.")
        super().__init__()
        self.client = OpenAI(api_key=CONFIG.OPENAI_API_KEY)

    @staticmethod
    def get_instance() -> 'OpenAIApi':
        if OpenAIApi._instance is None:
            OpenAIApi._instance = OpenAIApi()
        return OpenAIApi._instance
    
    @rate_limit(class_scope=True)
    async def request(self, preset_name: str, user_message: str) -> Optional[str]:
        preset = await AIPreset.load(name=preset_name)
        completion = self.client.chat.completions.create(
            model=preset.model,
            messages=[
                {
                    "role": "system",
                    "content": preset.system
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=preset.temperature,
            max_tokens=preset.max_tokens,
            top_p=preset.top_p,
            frequency_penalty=preset.frequency_penalty,
            presence_penalty=preset.presence_penalty
        )
        return completion.choices[0].message.content
    
class AIPreset():
    instances: dict[str, 'AIPreset'] = {}

    def __init__(self, model: str, system: str, temperature: float, max_tokens: int = 256, top_p: float = 1, frequency_penalty: float = 0, presence_penalty: float = 0) -> None:
        self.model = model
        self.system = system
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    @staticmethod
    async def load(name: str) -> 'AIPreset':
        if name in AIPreset.instances:
            return AIPreset.instances.get(name) # type: ignore
        
        path = PRESETS_FILE_PATH.format(name=name)
        data = file_to_dict(file_path=path)
        try:
            preset = AIPreset(**data)
        except Exception as e:
            raise RuntimeError(f"Preset {name} is invalid: {e}")
        
        AIPreset.instances[name] = preset
        return preset