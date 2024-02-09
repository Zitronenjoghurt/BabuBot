import aiohttp
import asyncio

class AbstractApiController():
    CALLS = 0
    SECONDS = 0
    BASE_URL = ""

    def __init__(self) -> None:
        # When the first call of a certain method was made since last reset
        self.first_method_call: dict[str, float] = {}

        # How many times the method was called since last reset
        self.method_count: dict[str, int] = {}

    def generate_url(self, endpoint: str, **kwargs) -> str:
        arguments = "&".join([f"{key}={value}" for key, value in kwargs.items()])
        return f"{self.BASE_URL}/{endpoint}?{arguments}"
    
    async def request(self, endpoint: str, expected_codes: list[int], **params) -> dict:
        url = self.generate_url(endpoint, **params)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status not in expected_codes:
                    data = await response.text()
                    raise UnexpectedResponseCodeError(url, response.status, data)
                else:
                    return await response.json()

class UnexpectedResponseCodeError(Exception):
    """Exception raised for unexpected response codes."""
    def __init__(self, url: str, status_code: int, response_body: str = "") -> None:
        self.url = url
        self.status_code = status_code
        self.response_body = response_body
        message = f"Unexpected response code {status_code} for URL: {url}."
        if response_body:
            message += f" Response body: {response_body}"
        super().__init__(message)