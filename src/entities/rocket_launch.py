import discord
from datetime import datetime, timedelta
from typing import Optional
from src.constants.config import Config
from src.entities.abstract_database_entity import AbstractDatabaseEntity
from src.entities.rocket import Rocket
from src.entities.rocket_launch_mission import RocketLaunchMission
from src.entities.rocket_launch_mission_agency import RocketLaunchMissionAgency
from src.entities.rocket_launch_pad import RocketLaunchPad
from src.entities.rocket_launch_status import RocketLaunchStatus
from src.utils.string_operations import limit_length
from src.utils.discord_time import relative_time, long_date_time, long_time

CONFIG = Config.get_instance()

class RocketLaunch(AbstractDatabaseEntity):
    TABLE_NAME = "rocket_launches"
    SERIALIZED_PROPERTIES = ["id", "created_stamp", "launch_id", "name", "last_updated", "status", "rocket", "net", "window_start", "window_end", "launch_service_provider", "launch_service_type", "weather_concerns", "hold_reason", "fail_reason", "mission", "mission_agencies", "pad", "webcast_live", "image_url", "orbital_launch_attempt_count", "orbital_launch_attempt_count_year", "vid_urls", "today_notification_sent", "soon_notification_sent", "liftoff_notification_sent", "botched_launch"]
    SERIALIZE_CLASSES = {"status": RocketLaunchStatus, "rocket": Rocket, "mission": RocketLaunchMission, "mission_agencies": RocketLaunchMissionAgency, "pad": RocketLaunchPad}
    SAVED_PROPERTIES = ["launch_id", "name", "last_updated", "status", "rocket", "net", "window_start", "window_end", "launch_service_provider", "launch_service_type", "weather_concerns", "hold_reason", "fail_reason", "mission", "mission_agencies", "pad", "webcast_live", "image_url", "orbital_launch_attempt_count", "orbital_launch_attempt_count_year", "vid_urls", "today_notification_sent", "soon_notification_sent", "liftoff_notification_sent", "botched_launch"]

    def __init__(
            self, 
            id: Optional[int] = None,
            created_stamp: Optional[float] = None,
            launch_id: Optional[str] = None,
            name: Optional[str] = None,
            last_updated: Optional[float] = None,
            status: Optional[RocketLaunchStatus] = None,
            rocket: Optional[Rocket] = None,
            mission: Optional[RocketLaunchMission] = None,
            mission_agencies: Optional[list[RocketLaunchMissionAgency]] = None,
            pad: Optional[RocketLaunchPad] = None,
            net: Optional[float] = None,
            window_start: Optional[float] = None,
            window_end: Optional[float] = None,
            launch_service_provider: Optional[str] = None,
            launch_service_type: Optional[str] = None,
            weather_concerns: Optional[str] = None,
            hold_reason: Optional[str] = None,
            fail_reason: Optional[str] = None,
            webcast_live: Optional[bool] = None,
            image_url: Optional[str] = None,
            orbital_launch_attempt_count: Optional[int] = None,
            orbital_launch_attempt_count_year: Optional[int] = None,
            notifications_sent: Optional[int] = None, # To be removed soon
            vid_urls: Optional[list[str]] = None,
            today_notification_sent: Optional[bool] = None,
            soon_notification_sent: Optional[bool] = None,
            liftoff_notification_sent: Optional[bool] = None,
            botched_launch: Optional[bool] = None
        ) -> None:
        super().__init__(id=id, created_stamp=created_stamp)
        self.launch_id = launch_id if isinstance(launch_id, str) else "No ID"
        self.name = name if isinstance(name, str) else "No Name"
        self.last_updated = last_updated if isinstance(last_updated, float) else 0.0
        self.status = status if isinstance(status, RocketLaunchStatus) else RocketLaunchStatus()
        self.rocket = rocket if isinstance(rocket, Rocket) else Rocket()
        self.mission = mission if isinstance(mission, RocketLaunchMission) else RocketLaunchMission()
        self.mission_agencies = mission_agencies if isinstance(mission_agencies, list) else []
        self.pad = pad if isinstance(pad, RocketLaunchPad) else RocketLaunchPad()
        self.net = net if isinstance(net, float) else 0.0
        self.window_start = window_start if isinstance(window_start, float) else 0.0
        self.window_end = window_end if isinstance(window_end, float) else 0.0
        self.launch_service_provider = launch_service_provider if isinstance(launch_service_provider, str) else "Unknown launch service provider"
        self.launch_service_type = launch_service_type if isinstance(launch_service_type, str) else "Unknown launch service type"
        self.weather_concerns = weather_concerns if isinstance(weather_concerns, str) else "No Concerns"
        self.hold_reason = hold_reason if isinstance(hold_reason, str) else "No Reason"
        self.fail_reason = fail_reason if isinstance(fail_reason, str) else "No Reason"
        self.webcast_live = webcast_live if isinstance(webcast_live, bool) else False
        self.image_url = image_url if isinstance(image_url, str) else None
        self.orbital_launch_attempt_count = orbital_launch_attempt_count if isinstance(orbital_launch_attempt_count, int) else 0
        self.orbital_launch_attempt_count_year = orbital_launch_attempt_count_year if isinstance(orbital_launch_attempt_count_year, int) else 0
        self.notifications_sent = notifications_sent if isinstance(notifications_sent, int) else 0 # To be removed soon
        self.vid_urls = vid_urls if isinstance(vid_urls, list) else []
        self.today_notification_sent = today_notification_sent if isinstance(today_notification_sent, bool) else False
        self.soon_notification_sent = soon_notification_sent if isinstance(soon_notification_sent, bool) else False
        self.liftoff_notification_sent = liftoff_notification_sent if isinstance(liftoff_notification_sent, bool) else False
        self.botched_launch = botched_launch if isinstance(botched_launch, bool) else False

    @staticmethod
    async def from_api_data(data: dict) -> 'RocketLaunch':
        launch_id = data.get("id", None)
        if launch_id is None:
            raise RuntimeError(f"An error occured while creating RocketLaunch from Api data: launch id is mandatory, but data did not include any!")
        
        existing_entry = await RocketLaunch.find(launch_id=launch_id)
        if isinstance(existing_entry, RocketLaunch):
            id = existing_entry.id
            created_stamp = existing_entry.created_stamp
            notifications_sent = existing_entry.notifications_sent # To be removed soon
            today_notification_sent = existing_entry.today_notification_sent
            soon_notification_sent = existing_entry.soon_notification_sent
            liftoff_notification_sent = existing_entry.liftoff_notification_sent
            botched_launch = existing_entry.botched_launch
        else:
            id = None
            created_stamp = None
            notifications_sent = None # To be removed soon
            today_notification_sent = None
            soon_notification_sent = None
            liftoff_notification_sent = None
            botched_launch = None

        name = data.get("name", "No Name")
        weather_concerns = data.get("weather_concerns", None)
        hold_reason = data.get("holdreason", None)
        fail_reason = data.get("failreason", None)
        webcast_live = data.get("webcast_live", None)
        image_url = data.get("image", None)
        orbital_launch_attempt_count = data.get("orbital_launch_attempt_count", None)
        orbital_launch_attempt_count_year = data.get("orbital_launch_attempt_count_year", None)
        vid_urls = data.get("vid_urls", None)

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

        mission_data = data.get("mission", {})
        if not isinstance(mission_data, dict):
            mission_data = {}
        mission = RocketLaunchMission.from_api_data(data=mission_data)

        agencies_data = mission_data.get("agencies", [])
        if not isinstance(agencies_data, list):
            agencies_data = []
        mission_agencies = [RocketLaunchMissionAgency.from_api_data(data=agency_data) for agency_data in agencies_data]

        pad_data = data.get("pad", {})
        if not isinstance(pad_data, dict):
            pad_data = {}
        pad = RocketLaunchPad.from_api_data(data=pad_data)

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
            mission=mission,
            mission_agencies=mission_agencies,
            pad=pad,
            net=net_stamp,
            window_start=window_start_stamp,
            window_end=window_end_stamp,
            launch_service_provider=launch_service_provider,
            launch_service_type=launch_service_type,
            weather_concerns=weather_concerns,
            hold_reason=hold_reason,
            fail_reason=fail_reason,
            webcast_live=webcast_live,
            image_url=image_url,
            orbital_launch_attempt_count=orbital_launch_attempt_count,
            orbital_launch_attempt_count_year=orbital_launch_attempt_count_year,
            notifications_sent=notifications_sent, # To be removed soon
            vid_urls=vid_urls,
            today_notification_sent=today_notification_sent,
            soon_notification_sent=soon_notification_sent,
            liftoff_notification_sent=liftoff_notification_sent,
            botched_launch=botched_launch
        )
    
    def is_go_confirmed(self) -> bool:
        return self.status.is_go_confirmed()
    
    def launches_in(self) -> timedelta:
        now_stamp = datetime.now().timestamp()
        seconds_left = self.net - now_stamp
        return timedelta(seconds=seconds_left)

    def launches_in_12h(self) -> bool:
        if not self.is_go_confirmed():
            return False
        launch_in = self.launches_in()
        return launch_in < timedelta(hours=12)
    
    def launches_in_10min(self) -> bool:
        if not self.is_go_confirmed():
            return False
        launch_in = self.launches_in()
        return launch_in < timedelta(minutes=10)
    
    def launch_successful(self) -> bool:
        return self.status.is_successful()
    
    def launch_failure(self) -> bool:
        return self.status.is_failure()
    
    def notify_launching_today(self) -> bool:
        return self.launches_in_12h() and not self.today_notification_sent
    
    def notify_launching_soon(self) -> bool:
        return self.launches_in_10min() and not self.soon_notification_sent
    
    def notify_liftoff_status(self) -> bool:
        return (self.launch_successful or self.launch_failure) and not self.liftoff_notification_sent
    
    def should_remove_entry(self) -> bool:
        # ToDo find out optimal parameters to find out which entries should be removed from the database
        return False
    
    def has_mission_agency(self) -> bool:
        return len(self.mission_agencies) > 0

    def get_mission_agency_name(self) -> Optional[str]:
        if not self.has_mission_agency():
            return None
        agency = self.mission_agencies[0]
        return agency.name
    
    def get_mission_agency_url(self) -> Optional[str]:
        if not self.has_mission_agency():
            return None
        agency = self.mission_agencies[0]
        if agency.info_url:
            return agency.info_url
        if agency.wiki_url:
            return agency.wiki_url
        return None
    
    def get_mission_agency_logo_url(self) -> Optional[str]:
        if not self.has_mission_agency():
            return None
        agency = self.mission_agencies[0]
        return agency.logo_url
    
    def get_launch_stamp(self) -> datetime:
        return datetime.fromtimestamp(self.net)
    
    def get_description_with_name(self) -> str:
        return f"**{limit_length(self.name, 256)}**\n*{limit_length(self.mission.description, 1000)}*"

    def generate_today_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="ROCKET LAUNCH NEWS", 
            description=self.get_description_with_name(),
            color=discord.Color.from_str("#5380B8"),
            timestamp=self.get_launch_stamp()
        )
        if self.image_url:
            embed.set_image(url=self.image_url)
        if self.get_mission_agency_name():
            embed.set_author(name=self.get_mission_agency_name(), icon_url=self.get_mission_agency_logo_url(), url=self.get_mission_agency_url())
        embed.add_field(name="Launch time", value=f"{relative_time(int(self.net))}\n{long_date_time(int(self.net))}")
        embed.add_field(name="Launch Service Provider", value=f"**`{self.launch_service_provider}`**")
        embed.add_field(name="Launch Vehicle", value=f"**`{self.rocket.full_name}`**")
        embed.add_field(name="Target Orbit", value=f"**`{self.mission.target_orbit}`**")
        embed.add_field(name="Number of launch", value=f"**`#{self.orbital_launch_attempt_count_year} this year`**\n**`#{self.orbital_launch_attempt_count} all time`**")
        embed.add_field(name="Launch Location", value=f"**`{self.pad.name}`**\n**`{self.pad.location_name}`**", inline=False)
        return embed
    
    def generate_soon_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="LAUNCHING SOON!", 
            description=self.get_description_with_name(),
            color=discord.Color.from_str("#ED4021"),
            timestamp=self.get_launch_stamp()
        )
        if self.image_url:
            embed.set_image(url=self.image_url)
        if self.get_mission_agency_name():
            embed.set_author(name=self.get_mission_agency_name(), icon_url=self.get_mission_agency_logo_url(), url=self.get_mission_agency_url())
        embed.add_field(name="Launch time", value=f"{relative_time(int(self.net))}\n{long_time(int(self.net))}", inline=False)
        embed.add_field(name="Launch Vehicle", value=f"**`{self.rocket.full_name}`**", inline=False)
        embed.add_field(name="Launch Location", value=f"**`{self.pad.name}`**\n**`{self.pad.location_name}`**", inline=False)
        if self.webcast_live and self.vid_urls:
            embed.add_field(name="Livestream", value=f"{self.vid_urls[0]}")
        elif self.webcast_live and self.mission.vid_urls:
            embed.add_field(name="Livestream", value=f"{self.mission.vid_urls[0]}")
        else:
            embed.add_field(name="Livestream unavailable", value="*We currently have no livestream URL, please check the official channels of the space agency.*")
        return embed
    
    def generate_success_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="LAUNCH SUCCESSFUL", 
            description=self.get_description_with_name(),
            color=discord.Color.green(),
            timestamp=self.get_launch_stamp()
        )
        if self.image_url:
            embed.set_image(url=self.image_url)
        if self.get_mission_agency_name():
            embed.set_author(name=self.get_mission_agency_name(), icon_url=self.get_mission_agency_logo_url(), url=self.get_mission_agency_url())
        return embed
    
    def generate_failure_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="LAUNCH FAILED", 
            description=self.get_description_with_name(),
            color=discord.Color.red(),
            timestamp=self.get_launch_stamp()
        )
        if self.image_url:
            embed.set_image(url=self.image_url)
        if self.get_mission_agency_name():
            embed.set_author(name=self.get_mission_agency_name(), icon_url=self.get_mission_agency_logo_url(), url=self.get_mission_agency_url())
        reason = self.fail_reason if self.fail_reason else "Unknown"
        embed.add_field(name="Reason", value=reason)
        return embed

    def generate_liftoff_status_embed(self) -> Optional[discord.Embed]:
        if self.launch_successful():
            return self.generate_success_embed()
        if self.launch_failure():
            return self.generate_failure_embed()
        
    def generate_hold_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="ON HOLD",
            description=self.get_description_with_name(),
            color=discord.Color.yellow()
        )
        if self.get_mission_agency_name():
            embed.set_author(name=self.get_mission_agency_name(), icon_url=self.get_mission_agency_logo_url(), url=self.get_mission_agency_url())
        if self.hold_reason:
            embed.add_field(name="Reason", value=self.hold_reason)
        embed.set_footer(text="After the failed launch attempt the launch sequence is on hold.")
        return embed
    
    def generate_tbc_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="LAUNCH WINDOW TBC",
            description=self.get_description_with_name(),
            color=discord.Color.light_gray()
        )
        if self.get_mission_agency_name():
            embed.set_author(name=self.get_mission_agency_name(), icon_url=self.get_mission_agency_logo_url(), url=self.get_mission_agency_url())
        if self.hold_reason:
            embed.add_field(name="Hold Reason", value=self.hold_reason, inline=False)
        embed.add_field(name="Potential New Launch Time", value=f"{relative_time(int(self.net))}\n{long_date_time(int(self.net))}")
        embed.set_footer(text="After the failed launch attempt the new launch window is awaiting confirmation.")
        return embed
    
    def generate_go_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="NEW LAUNCH WINDOW CONFIRMED",
            description=self.get_description_with_name(),
            color=discord.Color.green()
        )
        if self.get_mission_agency_name():
            embed.set_author(name=self.get_mission_agency_name(), icon_url=self.get_mission_agency_logo_url(), url=self.get_mission_agency_url())
        if self.hold_reason:
            embed.add_field(name="Hold Reason", value=self.hold_reason, inline=False)
        if self.fail_reason:
            embed.add_field(name="Fail Reason", value=self.fail_reason, inline=False)
        embed.add_field(name="Launch Time", value=f"{relative_time(int(self.net))}\n{long_date_time(int(self.net))}")
        embed.set_footer(text="After the failed launch attempt the new launch window was confirmed.")
        return embed