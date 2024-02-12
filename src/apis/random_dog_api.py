import aiohttp
import asyncio
import discord
import random
from src.apis.abstract_api_controller import ApiError, UnexpectedResponseCodeError
from src.apis.abstract_embed_api import AbstractEmbedApi
from src.apis.rate_limiting import rate_limit
from src.constants.config import Config
from src.logging.logger import LOGGER

CONFIG = Config.get_instance()

class RandomDogApi(AbstractEmbedApi):
    _instance = None
    CALLS = 1
    SECONDS = 5
    BASE_URL = "https://random.dog"

    def __init__(self) -> None:
        if RandomDogApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of RandomDogApi.")
        super().__init__()
        self.dog_index = []
        self.dog_count = 0
        self.initialized = False
        self.fetching = False

    @staticmethod
    def get_instance() -> 'RandomDogApi':
        if RandomDogApi._instance is None:
            RandomDogApi._instance = RandomDogApi()
        return RandomDogApi._instance
    
    @rate_limit(class_scope=True)
    async def _initialize_dog_index(self) -> None:
        self.fetching = True
        try:
            results = await self.request(endpoint="doggos", expected_codes=[200])
            if isinstance(results, list):
                for dog_image_url in results:
                    if isinstance(dog_image_url, str) and ("jpg" in dog_image_url or "png" in dog_image_url):
                        self.dog_index.append(dog_image_url)
                self.dog_count = len(self.dog_index)
                LOGGER.info(f"Successfully collected URL of {self.dog_count} dog images from random.dog.")
            else:
                LOGGER.error(f"No list was returned while trying to collect dog image URLs from random.dog.")
            self.initialized = True
            self.fetching = False
        except UnexpectedResponseCodeError as e:
            LOGGER.error(f"An unexpected response code was returned while trying to collect dog image URLs from random.dog: {e}")
        except asyncio.TimeoutError as e:
            LOGGER.error(f"A timeout happened while trying to collect dog image URLs from random.dog: {e}")
        except aiohttp.ClientConnectionError as e:
            LOGGER.error(f"A connection error occured while trying to collect dog image URLs from random.dog: {e}")

    async def get_image(self) -> str:
        if self.fetching:
            raise ApiError("The bot is currently fetching dog images, please wait a few seconds.")
        if not self.initialized:
            await self._initialize_dog_index()
        if self.dog_count == 0:
            raise ApiError("The bot was unable to retrieve any dog images from random.dog, please contact the developer.")
        random_index = random.randint(0, self.dog_count - 1)
        return f"https://random.dog/{self.dog_index[random_index]}"
    
    async def generate_embed(self) -> discord.Embed:
        url = await self.get_image()

        embed = discord.Embed(
            title="A RANDOM DOG :O",
            color=discord.Color.from_str("#d4904c")
        )
        embed.set_author(name="Doggy!", icon_url="https://random.dog/99922971-447f-4785-b5fe-db96f9938994.jpg", url="https://random.dog")
        embed.set_image(url=url)
        embed.set_footer(text=f"{self.dog_count} images provided by random.dog")
        return embed