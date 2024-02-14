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

class RandomCatApi(AbstractEmbedApi):
    _instance = None
    CALLS = 1
    SECONDS = 720
    BASE_URL = "https://api.thecatapi.com"

    def __init__(self) -> None:
        if RandomCatApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of RandomCatApi.")
        super().__init__()
        self.cat_queue = asyncio.Queue()
        self.fetching = False

    @staticmethod
    def get_instance() -> 'RandomCatApi':
        if RandomCatApi._instance is None:
            RandomCatApi._instance = RandomCatApi()
        return RandomCatApi._instance
    
    async def random_image(self) -> str:
        if self.cat_queue.empty():
            await self.cache_new_images()
        if self.cat_queue.empty():
            raise ApiError("The bot was unable to retrieve new cat images images, please contact the developer.")
        
        image_url: str = await self.cat_queue.get()
        LOGGER.debug(f"Successfully retrieved a cat image from cache, {self.cat_queue.qsize()} entries left.")

        # Preemptively refill cache if close to being empty
        if self.cat_queue.qsize() <= 10:
            asyncio.create_task(self.cache_new_images())
        return image_url
    
    @rate_limit(class_scope=True)
    async def cache_new_images(self) -> None:
        if self.fetching:
            raise ApiError("The bot is currently fetching more cat images, please wait a few seconds.")
        self.fetching = True
        try:
            results = await self.request(endpoint="v1/images/search", expected_codes=[200], api_key=CONFIG.CAT_API_KEY, limit=100)
            if isinstance(results, list):
                count = 0
                for entry in results:
                    url = entry.get("url", None)
                    if url:
                        await self.cat_queue.put(url)
                        count += 1
                LOGGER.info(f"Successfully collected {count} new cat images from thecatapi.")
            else:
                LOGGER.error(f"No list was returned while trying to cache new cat images.")
            self.fetching = False
        except UnexpectedResponseCodeError as e:
            self.fetching = False
            LOGGER.error(f"An unexpected response code was returned while trying to cache new cat images: {e}")
        except asyncio.TimeoutError as e:
            self.fetching = False
            LOGGER.error(f"A timeout happened while trying to cache new cat images: {e}")
        except aiohttp.ClientConnectionError as e:
            self.fetching = False
            LOGGER.error(f"A connection error occured while trying to cache new cat images: {e}")
    
    async def generate_embed(self) -> discord.Embed:
        url = await self.random_image()

        embed = discord.Embed(
            title="A RANDOM CAT!",
            color=discord.Color.from_str("#db7eed")
        )
        embed.set_author(name="KITTY :o", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Stray_kitten_Rambo002.jpg/440px-Stray_kitten_Rambo002.jpg", url="https://thecatapi.com")
        embed.set_image(url=url)
        embed.set_footer(text=f"over 60k images provided by thecatapi.com")
        return embed