import aiohttp
import asyncio
from src.apis.abstract_api_controller import AbstractApiController, UnexpectedResponseCodeError
from src.apis.rate_limiting import rate_limit
from src.logging.logger import LOGGER

class QuizApi(AbstractApiController):
    _instance = None
    CALLS = 1
    SECONDS = 5
    BASE_URL = "https://opentdb.com"

    def __init__(self) -> None:
        if QuizApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of QuizApi.")
        super().__init__()
        self.session_token = ""

    @staticmethod
    async def get_instance() -> 'QuizApi':
        if QuizApi._instance is None:
            QuizApi._instance = QuizApi()
            await QuizApi._instance._initialize_session_token()
        return QuizApi._instance
    
    @rate_limit(class_scope=True)
    async def _initialize_session_token(self) -> None:
        if len(self.session_token) > 0:
            return
        try:
            result = await self.request(endpoint="api_token.php", expected_codes=[200], command="request")
            token = result.get("token", None)
            if not token:
                LOGGER.error("The token request returned OK but still unable to retrieve session token for Quiz API (opentdb.com), proceeding without a token.")
                return
            self.session_token = token
            LOGGER.info("Successfully retrieved session token for Quiz API (opentdb.com).")
        except UnexpectedResponseCodeError as e:
            LOGGER.error(f"Unable to retrieve session token for Quiz API (opentdb.com) because of unexpected response code, proceeding without a token: {e}")
        except asyncio.TimeoutError as e:
            LOGGER.error(f"Unable to retrieve session token for Quiz API (opentdb.com) because of a TIMEOUT, proceeding without a token: {e}")
        except aiohttp.ClientConnectionError as e:
            LOGGER.error(f"Unable to retrieve session token for Quiz API (opentdb.com) because of a client connection error, proceeding without a token: {e}")