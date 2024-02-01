from src.utils.validator import validate_of_type

def retrieve_data(data: dict, keys: list[str]) -> dict:
    result = {}
    for key in keys:
        value = data.get(key, None)
        result[key] = value
    return result

def retrieve_data_safely(data: dict, key_types: dict) -> dict:
    result = {}
    for key, key_type in key_types.items():
        value = data.get(key, None)
        validate_of_type(value, key_type, key)
        result[key] = value
    return result