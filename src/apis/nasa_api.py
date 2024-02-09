import aiohttp
import asyncio
from datetime import datetime
from typing import Optional
from src.apis.abstract_api_controller import AbstractApiController, ApiError, UnexpectedResponseCodeError
from src.apis.rate_limiting import rate_limit
from src.constants.config import Config
from src.logging.logger import LOGGER
from src.utils.string_operations import limit_length

CONFIG = Config.get_instance()

class NasaApi(AbstractApiController):
    _instance = None
    CALLS = 5
    SECONDS = 20
    BASE_URL = "https://api.nasa.gov"

    def __init__(self) -> None:
        if NasaApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of ApodApi.")
        super().__init__()
        self.apod_queue = asyncio.Queue()

    @staticmethod
    def get_instance() -> 'NasaApi':
        if NasaApi._instance is None:
            NasaApi._instance = NasaApi()
        return NasaApi._instance
    
    # Retrieves a random "Astronomy Picture Of The Day" (APOD)
    # Will always request 50 pictures at once and save them in a queue
    async def random_apod(self) -> 'APOD':
        if self.apod_queue.empty():
            await self.cache_new_apod()
        if self.apod_queue.empty():
            raise ApiError("The bot was unable to retrieve new APOD images, please contact the developer.")
        apod: APOD = await self.apod_queue.get()
        LOGGER.debug(f"Successfully retrieved an APOD from cache, {self.apod_queue.qsize()} entries left.")
        return apod
    
    @rate_limit(class_scope=True)
    async def cache_new_apod(self) -> None:
        try:
            results = await self.request(endpoint="planetary/apod", expected_codes=[200], api_key=CONFIG.NASA_API_KEY, count=50)
            if isinstance(results, list):
                for apod_data in results:
                    await self.apod_queue.put(APOD.from_dict(apod_data))
                LOGGER.info(f"Successfully collected 50 new APOD from the NASA API.")
            else:
                LOGGER.error(f"No list was returned while trying to cache new APOD.")
        except UnexpectedResponseCodeError as e:
            LOGGER.error(f"An unexpected response code was returned while trying to cache new APOD: {e}")
        except asyncio.TimeoutError as e:
            LOGGER.error(f"A timeout happened while trying to cache new APOD: {e}")
        except aiohttp.ClientConnectionError as e:
            LOGGER.error(f"A connection error occured while trying to cache new APOD: {e}")

class APOD():
    def __init__(
            self,
            title: Optional[str] = None,
            description: Optional[str] = None,
            date: Optional[str] = None, #YYYY-MM-DD
            url: Optional[str] = None,
            copyright: Optional[str] = None
        ) -> None:
        self.title = title if title is not None else "No Title"
        self.description = description if description is not None else "No Description"
        self.date = date if isinstance(date, str) else ""
        self.url = url if url is not None else ""
        self.copyright = copyright if copyright is not None else "None"

        # Limit title and description so they fit in a discord embed
        self.title = limit_length(self.title, 250)
        self.description = limit_length(self.description, 2000)

    @staticmethod
    def from_dict(data: dict) -> 'APOD':
        title = data.get("title", None)
        description = data.get("explanation", None)
        date = data.get("date", None)
        copyright = data.get("copyright", None)

        url = data.get("hdurl", None)
        if not url:
            url = data.get("url", None)
        
        return APOD(
            title=title,
            description=description,
            date=date,
            copyright=copyright,
            url=url
        )