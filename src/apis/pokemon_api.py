import aiohttp
import asyncio
from typing import Optional
from src.apis.abstract_api_controller import AbstractApiController, UnexpectedResponseCodeError
from src.apis.rate_limiting import rate_limit
from src.constants.config import Config
from src.logging.logger import LOGGER
from src.utils.dict_operations import get_safe_from_path

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
    
    @rate_limit(calls=5, seconds=5)
    async def get_pokemon_data(self, name: str) -> Optional[dict]:
        general = await self.data_request(endpoint=f"api/v2/pokemon/{name}", data_name="general")
        if not general:
            return
        id = general.get("id", None)
        if not id:
            return
        
        species = await self.data_request(endpoint=f"api/v2/pokemon-species/{name}", data_name="species")
        if isinstance(species, dict):
            general["species"] = species
            evolution_chain_url = get_safe_from_path(species, ["evolution_chain", "url"])
            if isinstance(evolution_chain_url, str):
                general["evolution_chain_url"] = evolution_chain_url

        return general
    
    @rate_limit(calls=5, seconds=5)
    async def get_evolution_chain_data(self, id: int) -> Optional[dict]:
        return await self.data_request(endpoint=f"api/v2/evolution-chain/{id}", data_name="evolution")
    
    @rate_limit(calls=5, seconds=5)
    async def get_ability_data(self, name: str) -> Optional[dict]:
        return await self.data_request(endpoint=f"api/v2/ability/{name}", data_name="ability")
    
    @rate_limit(calls=10, seconds=3)
    async def get_move_data(self, name: str) -> Optional[dict]:
        return await self.data_request(endpoint=f"api/v2/move/{name}", data_name="move")

    @rate_limit(calls=25, seconds=5)
    async def data_request(self, endpoint: str, data_name: str, type = dict) -> Optional[dict]:
        try:
            result = await self.request(endpoint=endpoint, expected_codes=[200])
            if isinstance(result, type):
                return result
            else:
                LOGGER.error(f"No dict was returned while trying to fetch {data_name} pokemon data.")
        except UnexpectedResponseCodeError as e:
            LOGGER.error(f"An unexpected response code was returned while trying to fetch {data_name} pokemon data: {e}")
        except asyncio.TimeoutError as e:
            LOGGER.error(f"A timeout happened while trying to fetch {data_name} pokemon data: {e}")
        except aiohttp.ClientConnectionError as e:
            LOGGER.error(f"A connection error occured while trying to fetch {data_name} pokemon data: {e}")

def endpoint_from_url(url: str) -> str:
    return url[19:-1]