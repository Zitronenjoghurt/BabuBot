from datetime import datetime
from typing import Optional
from src.constants.config import Config
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.rocket import Rocket
from src.entities.rocket_launch_status import RocketLaunchStatus

CONFIG = Config.get_instance()

class RocketLaunch(AbstractDatabaseEntity):
    TABLE_NAME = "rocket_launches"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "launch_id", "name", "last_updated", "status", "rocket", "net", "window_start", "window_end", "launch_service_provider", "launch_service_type", "weather_concerns", "hold_reason", "fail_reason"]
    SERIALIZE_CLASSES = {"status": RocketLaunchStatus, "rocket": Rocket}
    SAVED_PROPERTIES = ["launch_id", "name", "last_updated", "status", "rocket", "net", "window_start", "window_end" "launch_service_provider", "launch_service_type", "weather_concerns", "hold_reason", "fail_reason"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            launch_id: Optional[str] = None,
            name: Optional[str] = None,
            last_updated: Optional[float] = None,
            status: Optional[RocketLaunchStatus] = None,
            rocket: Optional[Rocket] = None,
            net: Optional[float] = None,
            window_start: Optional[float] = None,
            window_end: Optional[float] = None,
            launch_service_provider: Optional[str] = None,
            launch_service_type: Optional[str] = None,
            weather_concerns: Optional[str] = None,
            hold_reason: Optional[str] = None,
            fail_reason: Optional[str] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        self.launch_id = launch_id if isinstance(launch_id, str) else "No ID"
        self.name = name if isinstance(name, str) else "No Name"
        self.last_updated = last_updated if isinstance(last_updated, float) else 0.0
        self.rocket = rocket if isinstance(rocket, Rocket) else Rocket()
        self.status = status if isinstance(status, RocketLaunchStatus) else RocketLaunchStatus()
        self.net = net if isinstance(net, float) else 0.0
        self.window_start = window_start if isinstance(window_start, float) else 0.0
        self.window_end = window_end if isinstance(window_end, float) else 0.0
        self.launch_service_provider = launch_service_provider if isinstance(launch_service_provider, str) else "Unknown launch service provider"
        self.launch_service_type = launch_service_type if isinstance(launch_service_type, str) else "Unknown launch service type"
        self.weather_concerns = weather_concerns if isinstance(weather_concerns, str) else "No Concerns"
        self.hold_reason = hold_reason if isinstance(hold_reason, str) else "No Reason"
        self.fail_reason = fail_reason if isinstance(fail_reason, str) else "No Reason"

    @staticmethod
    async def from_api_data(data: dict) -> 'RocketLaunch':
        launch_id = data.get("id", None)
        if launch_id is None:
            raise RuntimeError(f"An error occured while creating RocketLaunch from Api data: launch id is mandatory, but data did not include any!")
        
        existing_entry = await RocketLaunch.find(launch_id=launch_id)
        id = existing_entry.id if isinstance(existing_entry, RocketLaunch) else None
        created_stamp = existing_entry.created_stamp if isinstance(existing_entry, RocketLaunch) else None
        name = data.get("name", "No Name")
        weather_concerns = data.get("weather_concerns", None)
        hold_reason = data.get("holdreason", None)
        fail_reason = data.get("failreason", None)

        last_updated = data.get("last_updated", None)
        if isinstance(last_updated, str):
            last_updated = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
        last_updated_stamp = last_updated.timestamp() if isinstance(last_updated, datetime) else 0

        status_data = data.get("status", {})
        if not isinstance(status_data, dict):
            status_data = {}
        status = RocketLaunchStatus.from_api_data(data=status_data)

        rocket_data = data.get("rocket", {})
        if not isinstance(rocket_data, dict):
            rocket_data = {}
        rocket = Rocket.from_api_data(data=rocket_data)

        net = data.get("net", None)
        if isinstance(net, str):
            net = datetime.fromisoformat(net.replace('Z', '+00:00'))
        net_stamp = net.timestamp() if isinstance(net, datetime) else 0

        window_start = data.get("window_start", None)
        if isinstance(window_start, str):
            window_start = datetime.fromisoformat(window_start.replace('Z', '+00:00'))
        window_start_stamp = window_start.timestamp() if isinstance(window_start, datetime) else 0

        window_end = data.get("window_end", None)
        if isinstance(window_end, str):
            window_end = datetime.fromisoformat(window_end.replace('Z', '+00:00'))
        window_end_stamp = window_end.timestamp() if isinstance(window_end, datetime) else 0

        launch_service_data = data.get("launch_service_provider", {})
        if not isinstance(launch_service_data, dict):
            launch_service_data = {}
        launch_service_provider = launch_service_data.get("name", None)
        launch_service_type = launch_service_data.get("type", None)

        return RocketLaunch(
            id=id,
            created_stamp=created_stamp,
            launch_id=launch_id,
            name=name,
            last_updated=last_updated_stamp,
            status=status,
            rocket=rocket,
            net=net_stamp,
            window_start=window_start_stamp,
            window_end=window_end_stamp,
            launch_service_provider=launch_service_provider,
            launch_service_type=launch_service_type,
            weather_concerns=weather_concerns,
            hold_reason=hold_reason,
            fail_reason=fail_reason
        )