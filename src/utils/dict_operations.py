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

def sort_simple(data: dict, descending: bool) -> dict:
    return dict(sorted(data.items(), key=lambda item: item[1], reverse=descending))

# Recursively find the difference between two dictionaries, including nested dictionaries
def deep_difference(old_dict: dict, new_dict: dict) -> dict:
    changes = {}
    all_keys = old_dict.keys() | new_dict.keys()  # Union of keys from both dictionaries

    for key in all_keys:
        old_value = old_dict.get(key)
        new_value = new_dict.get(key)

        if old_value == new_value:
            continue

        # If both values are dicts, recurse. Otherwise record the change directly
        if isinstance(old_value, dict) and isinstance(new_value, dict):
            nested_changes = deep_difference(old_value, new_value)
            if nested_changes:
                changes[key] = nested_changes
        else:
            changes[key] = (old_value, new_value)

    return changes