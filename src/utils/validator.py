from typing import Any

def validate_of_type(value: Any, required_type: type, value_name: str = "value"):
    if not isinstance(value, required_type):
        raise ValueError(f"{value_name} must be of type {required_type.__name__}")