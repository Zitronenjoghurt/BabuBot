import asyncio
import math
from datetime import datetime, timedelta
from functools import wraps

def rate_limit(calls: int = 0, seconds: int = 0, class_scope: bool = False):
    """
    A decorator for rate limiting methods. Only supposed to be used on methods in classes implementing AbstractApiController.

    Parameters:
    - calls (int): The maximum number of calls allowed for the decorated method within the specified time frame.
    - seconds (int): The time frame in seconds within which the specified number of calls can be made.
    - class_scope (bool, optional): If True, this method shares a rate limit pool with equally decorated methods in the class.

    Returns:
    - A decorator that limits the rate at which the decorated method can be called.

    Raises:
    - RuntimeError: If `calls` or `seconds` is set to less than 1.
    """
    def decorator(method):
        @wraps(method)
        async def wrapper(self, *args, **kwargs):
            method_name = method.__name__
            if class_scope:
                method_name = "at-class-scope"
                _calls = self.CALLS
                _seconds = self.SECONDS
            else:
                _calls = calls
                _seconds = seconds

            if _calls < 1 or _seconds < 1:
                raise RuntimeError("Rate limit calls and seconds have to be greater or equal 1.")

            # Initialize method name in tracking dictionaries
            if method_name not in self.first_method_call:
                self.first_method_call[method_name] = 0
            if method_name not in self.method_count:
                self.method_count[method_name] = 0

            while True:
                # Reset if time of first call has passed
                if time_passed(self.first_method_call[method_name], _seconds):
                    self.first_method_call[method_name] = datetime.now().timestamp()
                    self.method_count[method_name] = 0

                # Check rate limit
                if self.method_count[method_name] < _calls:
                    self.method_count[method_name] += 1
                    break
                else:
                    cooldown = cooldown_time(timestamp=self.first_method_call[method_name], seconds=_seconds)
                    await asyncio.sleep(cooldown)

            return await method(self, *args, **kwargs)
        return wrapper
    return decorator

def time_passed(timestamp: float, seconds: int) -> bool:
    time = datetime.fromtimestamp(timestamp)
    now = datetime.now()

    if now - time >= timedelta(seconds=seconds):
        return True
    return False

def cooldown_time(timestamp: float, seconds: int) -> int:
    first_call = datetime.fromtimestamp(timestamp)
    now = datetime.now()

    seconds_passed = max(math.ceil((now - first_call).total_seconds()), 0)
    return seconds - seconds_passed