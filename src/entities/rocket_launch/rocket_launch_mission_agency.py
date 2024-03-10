from typing import Optional
from src.entities.abstract_serializable_entity import AbstractSerializableEntity

class RocketLaunchMissionAgency(AbstractSerializableEntity):
    SERIALIZED_PROPERTIES = ["name", "description", "type", "founding_year", "launchers", "total_launch_count", "consecutive_successful_launches", "successful_launches", "failed_launches", "pending_launches", "consecutive_successful_landings", "successful_landings", "failed_landings", "attempted_landings", "info_url", "wiki_url", "logo_url", "image_url"]

    def __init__(
            self, 
            name: Optional[str] = None,
            description: Optional[str] = None,
            type: Optional[str] = None,
            founding_year: Optional[str] = None,
            launchers: Optional[str] = None,
            total_launch_count: Optional[int] = None,
            consecutive_successful_launches: Optional[int] = None,
            successful_launches: Optional[int] = None,
            failed_launches: Optional[int] = None,
            pending_launches: Optional[int] = None,
            consecutive_successful_landings: Optional[int] = None,
            successful_landings: Optional[int] = None,
            failed_landings: Optional[int] = None,
            attempted_landings: Optional[int] = None,
            info_url: Optional[str] = None,
            wiki_url: Optional[str] = None,
            logo_url: Optional[str] = None,
            image_url: Optional[str] = None
        ) -> None:
        self.name = name if isinstance(name, str) else "No Name"
        self.description = description if isinstance(description, str) else "No Description"
        self.type = type if isinstance(type, str) else "No Type"
        self.founding_year = founding_year if isinstance(founding_year, str) else "Unknown Year"
        self.launchers = launchers if isinstance(launchers, str) else "No Launchers"
        self.total_launch_count = total_launch_count if isinstance(total_launch_count, int) else None
        self.consecutive_successful_launches = consecutive_successful_launches if isinstance(consecutive_successful_launches, int) else None
        self.successful_launches = successful_launches if isinstance(successful_launches, int) else None
        self.failed_launches = failed_launches if isinstance(failed_launches, int) else None
        self.pending_launches = pending_launches if isinstance(pending_launches, int) else None
        self.consecutive_successful_landings = consecutive_successful_landings if isinstance(consecutive_successful_landings, int) else None
        self.successful_landings = successful_landings if isinstance(successful_landings, int) else None
        self.failed_landings = failed_landings if isinstance(failed_landings, int) else None
        self.attempted_landings = attempted_landings if isinstance(attempted_landings, int) else None
        self.info_url = info_url if isinstance(info_url, str) else None
        self.wiki_url = wiki_url if isinstance(wiki_url, str) else None
        self.logo_url = logo_url if isinstance(logo_url, str) else None
        self.image_url = image_url if isinstance(image_url, str) else None

    @staticmethod
    def from_api_data(data: dict) -> 'RocketLaunchMissionAgency':
        name = data.get("name", None)
        description = data.get("description", None)
        type = data.get("type", None)
        founding_year = data.get("founding_year", None)
        launchers = data.get("launchers", None)
        total_launch_count = data.get("total_launch_count", None)
        consecutive_successful_launches = data.get("consecutive_successful_launches", None)
        successful_launches = data.get("successful_launches", None)
        failed_launches = data.get("failed_launches", None)
        pending_launches = data.get("pending_launches", None)
        consecutive_successful_landings = data.get("consecutive_successful_landings", None)
        successful_landings = data.get("successful_landings", None)
        failed_landings = data.get("failed_landings", None)
        attempted_landings = data.get("attempted_landings", None)
        info_url = data.get("info_url", None)
        wiki_url = data.get("wiki_url", None)
        logo_url = data.get("logo_url", None)
        image_url = data.get("image_url", None)

        return RocketLaunchMissionAgency(
            name=name, 
            description=description, 
            type=type,
            founding_year=founding_year,
            launchers=launchers,
            total_launch_count=total_launch_count,
            consecutive_successful_launches=consecutive_successful_launches,
            successful_launches=successful_launches,
            failed_launches=failed_launches,
            pending_launches=pending_launches,
            consecutive_successful_landings=consecutive_successful_landings,
            successful_landings=successful_landings,
            failed_landings=failed_landings,
            attempted_landings=attempted_landings,
            info_url=info_url,
            wiki_url=wiki_url,
            logo_url=logo_url,
            image_url=image_url
        )