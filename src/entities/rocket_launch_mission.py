from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class RocketLaunchMission(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["name", "description", "type", "target_orbit", "target_orbit_abbreviation", "info_urls", "vid_urls"]

    def __init__(
            self, 
            name: Optional[str] = None,
            description: Optional[str] = None,
            type: Optional[str] = None,
            target_orbit: Optional[str] = None,
            target_orbit_abbreviation: Optional[str] = None,
            info_urls: Optional[list[str]] = None,
            vid_urls: Optional[list[str]] = None
        ) -> None:
        self.name = name if isinstance(name, str) else "No Name"
        self.description = description if isinstance(description, str) else "No Description"
        self.type = type if isinstance(type, str) else "No Type"
        self.target_orbit = target_orbit if isinstance(target_orbit, str) else "No target orbit"
        self.target_orbit_abbreviation = target_orbit_abbreviation if isinstance(target_orbit_abbreviation, str) else "No target orbit"
        self.info_urls = info_urls if isinstance(info_urls, list) else []
        self.vid_urls = vid_urls if isinstance(vid_urls, list) else []

    @staticmethod
    def from_api_data(data: dict) -> 'RocketLaunchMission':
        name = data.get("name", None)
        description = data.get("description", None)
        type = data.get("type", None)

        orbit_data = data.get("orbit", {})
        if not isinstance(orbit_data, dict):
            orbit_data = {}
        target_orbit = orbit_data.get("name", None)
        target_orbit_abbreviation = orbit_data.get("SSO", None)

        info_urls = data.get("info_urls", [])
        if not isinstance(info_urls, list):
            info_urls = []
        
        vid_urls = data.get("vid_urls", [])
        if not isinstance(vid_urls, list):
            vid_urls = []

        return RocketLaunchMission(
            name=name, 
            description=description, 
            type=type,
            target_orbit=target_orbit,
            target_orbit_abbreviation=target_orbit_abbreviation,
            info_urls=info_urls,
            vid_urls=vid_urls
        )