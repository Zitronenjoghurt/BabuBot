from typing import Any

def validate_of_type(value: Any, required_type: type, value_name: str = "value"):
    if not isinstance(value, required_type):
        raise ValueError(f"{value_name} must be of type {required_type.__name__}")
    
def validate_all_in_of_type(values: list, required_type: type, value_name: str = "value", list_name: str = "list"):
    for value in values:
        if not isinstance(value, required_type):
            raise ValueError(f"{value_name} in {list_name} must be of type {required_type.__name__}")