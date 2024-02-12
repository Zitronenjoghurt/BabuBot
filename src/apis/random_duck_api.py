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

class RandomDuckApi(AbstractEmbedApi):
    _instance = None
    CALLS = 1
    SECONDS = 5
    BASE_URL = "https://random-d.uk"

    def __init__(self) -> None:
        if RandomDuckApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of RandomDuckApi.")
        super().__init__()
        self.duck_index = []
        self.duck_count = 0
        self.initialized = False
        self.fetching = False

    @staticmethod
    def get_instance() -> 'RandomDuckApi':
        if RandomDuckApi._instance is None:
            RandomDuckApi._instance = RandomDuckApi()
        return RandomDuckApi._instance
    
    @rate_limit(class_scope=True)
    async def _initialize_duck_index(self) -> None:
        self.fetching = True
        try:
            result = await self.request(endpoint="api/v2/list", expected_codes=[200])
            if isinstance(result, dict):
                gifs = result.get("gifs", [])
                jpgs = result.get("images", [])
                self.duck_index.extend(gifs)
                self.duck_index.extend(jpgs)
                self.duck_count = len(gifs) + len(jpgs)
                LOGGER.info(f"Successfully collected URL of {self.duck_count} duck images from random-d.uk.")
            else:
                LOGGER.error(f"No dict was returned while trying to collect duck image URLs from random-d.uk.")
            self.initialized = True
            self.fetching = False
        except UnexpectedResponseCodeError as e:
            LOGGER.error(f"An unexpected response code was returned while trying to collect duck image URLs from random-d.uk: {e}")
        except asyncio.TimeoutError as e:
            LOGGER.error(f"A timeout happened while trying to collect duck image URLs from random-d.uk: {e}")
        except aiohttp.ClientConnectionError as e:
            LOGGER.error(f"A connection error occured while trying to collect duck image URLs from random-d.uk: {e}")

    async def get_image(self) -> str:
        if self.fetching:
            raise ApiError("The bot is currently fetching duck images, please wait a few seconds.")
        if not self.initialized:
            await self._initialize_duck_index()
        if self.duck_count == 0:
            raise ApiError("The bot was unable to retrieve any duck images from random-d.uk, please contact the developer.")
        random_index = random.randint(0, self.duck_count - 1)
        return f"https://random-d.uk/api/{self.duck_index[random_index]}"
    
    async def generate_embed(self) -> discord.Embed:
        url = await self.get_image()

        embed = discord.Embed(
            title="A RANDOM DUCKY!",
            color=discord.Color.from_str("#edbe3b")
        )
        embed.set_author(name="DUCK!", icon_url="https://random-d.uk/api/188.jpg", url="https://random-d.uk")
        embed.set_image(url=url)
        embed.set_footer(text=f"{self.duck_count} images provided by random-d.uk")
        return embed