import aiohttp
import asyncio
from typing import Optional
from src.apis.abstract_api_controller import AbstractApiController, ApiError, UnexpectedResponseCodeError
from src.apis.rate_limiting import rate_limit
from src.constants.config import Config
from src.entities.rocket_launch import RocketLaunch
from src.logging.logger import LOGGER

CONFIG = Config.get_instance()

# Rate limit of 15 requests per hour
class LaunchLibrary2Api(AbstractApiController):
    _instance = None
    CALLS = 1
    SECONDS = 300
    BASE_URL = "https://ll.thespacedevs.com"

    def __init__(self) -> None:
        if LaunchLibrary2Api._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of LaunchLibrary2Api.")
        super().__init__()
        self.fetching = False

    @staticmethod
    def get_instance() -> 'LaunchLibrary2Api':
        if LaunchLibrary2Api._instance is None:
            LaunchLibrary2Api._instance = LaunchLibrary2Api()
        return LaunchLibrary2Api._instance
    
    async def _process_launches(self, data: dict) -> list[tuple[str, dict]]:
        results = data.get("results", [])

        all_updated_fields = []
        for result in results:
            # ToDo: Notify on certain updates, like when theres a new fail reason, etc.
            entry = await RocketLaunch.from_api_data(data=result)
            updated_fields = await entry.save()
            all_updated_fields.append((entry.launch_id, updated_fields))
        return all_updated_fields

    @rate_limit(class_scope=True)
    async def update_launches(self, limit: int = 100) -> Optional[list[tuple[str, dict]]]:
        if self.fetching:
            raise ApiError("The bot is currently fetching launches.")
        self.fetching = True
        try:
            data = await self.request(endpoint="2.2.0/launch/upcoming", expected_codes=[200], limit=limit)
            if isinstance(data, dict):
                updated_fields = await self._process_launches(data=data)
                LOGGER.info(f"Successfully updated launch entries from the LL2 API.")
                return updated_fields
            else:
                LOGGER.error(f"No dictionary was returned while trying to update launch entries.")
        except UnexpectedResponseCodeError as e:
            LOGGER.error(f"An unexpected response code was returned while trying to update launch entries: {e}")
        except asyncio.TimeoutError as e:
            LOGGER.error(f"A timeout happened while trying to update launch entries: {e}")
        except aiohttp.ClientConnectionError as e:
            LOGGER.error(f"A connection error occured while trying to update launch entries: {e}")
        self.fetching = False