import re
from typing import Optional

def limit_length(string: str, max_length: int) -> str:
    if len(string) > max_length:
        if max_length > 3:
            return string[:max_length-3] + "..."
        else:
            return string[:max_length]
    return string

def last_integer_from_url(url: str) -> Optional[int]:
    matches = re.findall(r'\d+', url)
    if not matches:
        return
    return int(matches[-1])

# Splits the string by hyphen and capitalizes each part
def format_name(string: str) -> str:
    parts = string.split('-')
    capitalized_parts = [part.capitalize() for part in parts]
    return ' '.join(capitalized_parts)