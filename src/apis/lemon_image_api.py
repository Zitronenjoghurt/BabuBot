import aiohttp
import asyncio
import discord
import random
from src.apis.abstract_api_controller import AbstractApiController, ApiError, UnexpectedResponseCodeError
from src.apis.rate_limiting import rate_limit
from src.constants.config import Config
from src.logging.logger import LOGGER

CONFIG = Config.get_instance()

CATEGORIES = ["hug", "kiss", "slap", "pat", "punch"]
CATEGORY_VERB = {
    "hug": "hugs",
    "kiss": "kisses",
    "slap": "slaps",
    "pat": "pats",
    "punch": "punches"
}
CATEGORY_COLOR = {
    "hug": "#F52547",
    "kiss": "#FC30AB",
    "slap": "#52B7C4",
    "pat": "#F26B49",
    "punch": "#B5040A"
}

class LemonImageApi(AbstractApiController):
    _instance = None
    CALLS = 10
    SECONDS = 60
    BASE_URL = "https://api.lemon.industries"

    def __init__(self) -> None:
        if LemonImageApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of LemonImageApi.")
        super().__init__()
        self.fetching = False
        self.initialized = False
        self.urls_by_category = {}
        self.category_counts = {}

    @staticmethod
    def get_instance() -> 'LemonImageApi':
        if LemonImageApi._instance is None:
            LemonImageApi._instance = LemonImageApi()
        return LemonImageApi._instance
    
    async def random_image(self, category: str) -> str:
        if not self.initialized:
            await self._initialize()
        if not self.initialized:
            raise ApiError("The bot was unable to retrieve the random gifs, please contact the developer.")
        
        category = category.lower()
        if category not in self.urls_by_category:
            raise ApiError("The given category does not exist.")
        
        category_count = self.category_counts[category]
        random_index = random.randint(0, category_count - 1)
        
        return self.urls_by_category[category][random_index]
    
    async def _initialize(self) -> None:
        if self.initialized:
            return
        if self.fetching:
            raise ApiError("The bot is currently initializing the random images, please wait a few seconds.")
        for category in CATEGORIES:
            await self._initialize_category(category=category)
        self.initialized = True
    
    @rate_limit(class_scope=True)
    async def _initialize_category(self, category: str) -> None:
        self.fetching = True
        try:
            result = await self.request(endpoint=f"images/{category}", expected_codes=[200])
            if isinstance(result, dict):
                base_url = result.get("base_url", None)
                if base_url is None:
                    self.fetching = False
                    return
                count = result.get("count", 0)
                image_names = result.get("image_names", [])
                self.urls_by_category[category] = [f"{base_url}{image_name}" for image_name in image_names]
                self.category_counts[category] = count
                LOGGER.info(f"Successfully collected {count} new {category} images from lemon api.")
            else:
                LOGGER.error(f"No list was returned while trying to collect {category} images from lemon api.")
            self.fetching = False
        except UnexpectedResponseCodeError as e:
            self.fetching = False
            LOGGER.error(f"An unexpected response code was returned while trying to collect {category} images from lemon api: {e}")
        except asyncio.TimeoutError as e:
            self.fetching = False
            LOGGER.error(f"A timeout happened while trying to collect {category} images from lemon api: {e}")
        except aiohttp.ClientConnectionError as e:
            self.fetching = False
            LOGGER.error(f"A connection error occured while trying to collect {category} images from lemon api: {e}")