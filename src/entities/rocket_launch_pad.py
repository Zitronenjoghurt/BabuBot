from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class RocketLaunchPad(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["name", "description", "info_url", "wiki_url", "map_url", "map_image_url", "latitude", "longitude", "location_name", "country_code", "total_launch_count"]

    def __init__(
            self, 
            name: Optional[str] = None,
            description: Optional[str] = None,
            info_url: Optional[str] = None,
            wiki_url: Optional[str] = None,
            map_url: Optional[str] = None,
            map_image_url: Optional[str] = None,
            latitude: Optional[str] = None,
            longitude: Optional[str] = None,
            location_name: Optional[str] = None,
            country_code: Optional[str] = None,
            total_launch_count: Optional[int] = None
        ) -> None:
        self.name = name if isinstance(name, str) else "No Name"
        self.description = description if isinstance(description, str) else "No Description"
        self.info_url = info_url if isinstance(info_url, str) else None
        self.wiki_url = wiki_url if isinstance(wiki_url, str) else None
        self.map_url = map_url if isinstance(map_url, str) else None
        self.map_image_url = map_image_url if isinstance(map_image_url, str) else None
        self.latitude = latitude if isinstance(latitude, str) else "Unknown"
        self.longitude = longitude if isinstance(longitude, str) else "Unknown"
        self.location_name = location_name if isinstance(location_name, str) else "No Location Name"
        self.country_code = country_code if isinstance(country_code, str) else "No Country Code"
        self.total_launch_count = total_launch_count if isinstance(total_launch_count, int) else 0

    @staticmethod
    def from_api_data(data: dict) -> 'RocketLaunchPad':
        name = data.get("name", None)
        description = data.get("description", None)
        info_url = data.get("info_url", None)
        wiki_url = data.get("wiki_url", None)
        map_url = data.get("map_url", None)
        map_image_url = data.get("map_image", None)
        latitude = data.get("latitude", None)
        longitude = data.get("longitude", None)
        country_code = data.get("country_code", None)
        total_launch_count = data.get("total_launch_count", None)

        location_data = data.get("location", {})
        if not isinstance(location_data, dict):
            location_data = {}
        location_name = location_data.get("name", None)

        return RocketLaunchPad(
            name=name, 
            description=description, 
            info_url=info_url,
            wiki_url=wiki_url,
            map_url=map_url,
            map_image_url=map_image_url,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            country_code=country_code,
            total_launch_count=total_launch_count
        )