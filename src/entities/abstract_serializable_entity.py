import json
from src.utils.dict_operations import retrieve_data

class AbstractSerializableEntity():
    SERIALIZED_PROPERTIES = []
    SERIALIZE_CLASSES = {}

    def to_dict(self) -> dict:
        data = {}
        for property in self.SERIALIZED_PROPERTIES:
            value = getattr(self, property)
            # Allows for serialization if value is a list of serializable entities
            if isinstance(value, list):
                new_value = []
                for list_value in value:
                    if hasattr(list_value, "to_dict"):
                        new_value.append(list_value.to_dict())
                    else:
                        new_value.append(list_value)
                value = new_value
            elif isinstance(value, dict):
                new_value = {}
                for dict_key, dict_value in value.items():
                    if hasattr(dict_value, "to_dict"):
                        dict_value = dict_value.to_dict()
                    new_value[dict_key] = dict_value
                value = new_value
            # Allows for nested serialization
            elif hasattr(value, "to_dict"):
                value = value.to_dict()
            data[property] = value
        return data
    
    @classmethod
    def from_dict(cls, data: dict):
        data = retrieve_data(data, cls.SERIALIZED_PROPERTIES)

        # Check for serialized properties that have to be serialized themself
        # Allows for nested deserialization
        for property, serialize_class in cls.SERIALIZE_CLASSES.items():
            if property in data:
                value = data[property]
                if value is None:
                    value = {}
                # If its a list of deserializable entities, handle it properly
                if isinstance(value, list):
                    data[property] = []
                    for list_value in value:
                        data[property].append(serialize_class.from_dict(list_value))
                elif isinstance(value, dict):
                    data[property] = {}
                    for dict_key, dict_value in value:
                        data[property][dict_key] = serialize_class.from_dict(dict_value)
                else:
                    data[property] = serialize_class.from_dict(value)
        return cls(**data)
    
    def to_json_string(self) -> str:
        data = self.to_dict()
        json_string = json.dumps(data, indent=4)
        return json_string