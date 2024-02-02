import json
from src.utils.dict_operations import retrieve_data

class AbstractSerializableEntity():
    SERIALIZED_PROPERTIES = []
    SERIALIZE_CLASSES = {}

    def to_dict(self) -> dict:
        data = {}
        for property in self.SERIALIZED_PROPERTIES:
            value = getattr(self, property)
            # Allows for nested serialization
            if hasattr(value, "to_dict"):
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
                data[property] = serialize_class.from_dict(value)
        return cls(**data)
    
    def to_json_string(self) -> str:
        data = self.to_dict()
        json_string = json.dumps(data, indent=4)
        return json_string