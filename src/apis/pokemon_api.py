import aiohttp
import asyncio
from typing import Optional
from src.apis.abstract_api_controller import AbstractApiController, UnexpectedResponseCodeError
from src.apis.rate_limiting import rate_limit
from src.constants.config import Config
from src.logging.logger import LOGGER

CONFIG = Config.get_instance()

class PokemonApi(AbstractApiController):
    _instance = None
    CALLS = 10
    SECONDS = 5
    BASE_URL = "https://pokeapi.co"

    def __init__(self) -> None:
        if PokemonApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of PokemonApi.")
        super().__init__()

    @staticmethod
    def get_instance() -> 'PokemonApi':
        if PokemonApi._instance is None:
            PokemonApi._instance = PokemonApi()
        return PokemonApi._instance
    
    @rate_limit(calls=10, seconds=5)
    async def get_pokemon_data(self, name: str) -> Optional[dict]:
        general = await self.get_general_data(name=name)
        if not general:
            return
        id = general.get("id", None)
        if not id:
            return

        # ToDo: fetch other data
        return general

    @rate_limit(calls=10, seconds=5)
    async def get_general_data(self, name: str) -> Optional[dict]:
        try:
            result = await self.request(endpoint=f"api/v2/pokemon/{name}", expected_codes=[200])
            if isinstance(result, dict):
                return result
            else:
                LOGGER.error(f"No dict was returned while trying to fetch general pokemon data.")
        except UnexpectedResponseCodeError as e:
            LOGGER.error(f"An unexpected response code was returned while trying to fetch general pokemon data: {e}")
        except asyncio.TimeoutError as e:
            LOGGER.error(f"A timeout happened while trying to fetch general pokemon data: {e}")
        except aiohttp.ClientConnectionError as e:
            LOGGER.error(f"A connection error occured while trying to fetch general pokemon data: {e}")