from discord.ext import commands
from src.apis.launch_library2_api import LaunchLibrary2Api
from src.entities.rocket_launch import RocketLaunch
from src.logging.logger import LOGGER

ACTIVE = True
INTERVAL_SECONDS = 300

LL2 = LaunchLibrary2Api.get_instance()

async def run(bot: commands.Bot):
    launch_and_updated_fields = await LL2.update_launches()
    if not launch_and_updated_fields:
        return
    
    for launch_id, fields in launch_and_updated_fields:
        status = fields.get("status", None)
        if status:
            await handle_status_change(bot=bot, launch_id=launch_id, status=status)

# Handle botched starts, holds on liftoff or other unexpected status updates
async def handle_status_change(bot: commands.Bot, launch_id: str, status: dict) -> None:
    abbrev: tuple[str, str] = status.get("abbreviation", None)
    if not isinstance(abbrev, tuple):
        return
    old_status, new_status = abbrev[0].lower(), abbrev[1].lower()

    if not old_status == "go":
        return

    if new_status == "hold":
        rocket_launch: RocketLaunch = await RocketLaunch.find(launch_id=launch_id)
        if not rocket_launch:
            return
        rocket_launch.soon_notification_sent = False
        rocket_launch.liftoff_notification_sent = False
        await rocket_launch.save()
        LOGGER.warning(f"ROCKET Detected a status change to hold after it was set to go from {rocket_launch.name} ({rocket_launch.id})")
    
    if new_status in ["tbc", "tbd"]:
        rocket_launch: RocketLaunch = await RocketLaunch.find(launch_id=launch_id)
        if not rocket_launch:
            return
        rocket_launch.today_notification_sent = False
        rocket_launch.soon_notification_sent = False
        rocket_launch.liftoff_notification_sent = False
        await rocket_launch.save()
        LOGGER.warning(f"ROCKET Detected a status change to {new_status} after it was set to go from {rocket_launch.name} ({rocket_launch.id})")