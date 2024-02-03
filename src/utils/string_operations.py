def limit_length(string: str, max_length: int) -> str:
    if len(string) > max_length:
        if max_length > 3:
            return string[:max_length-3] + "..."
        else:
            return string[:max_length]
    return string