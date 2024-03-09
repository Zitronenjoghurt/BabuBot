from discord.ext import commands
from src.apis.launch_library2_api import LaunchLibrary2Api
from src.constants.config import Config
from src.entities.rocket_launch import RocketLaunch
from src.logging.logger import LOGGER
from src.utils.bot_operations import send_in_channel

ACTIVE = True
INTERVAL_SECONDS = 300

CONFIG = Config.get_instance()
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

    if new_status in ["success", "failure"]:
        return

    rocket_launch: RocketLaunch = await RocketLaunch.find(launch_id=launch_id)
    if not rocket_launch:
        return
    
    if not old_status == "go" and not rocket_launch.botched_launch:
        return

    embed = None
    if new_status == "hold":
        rocket_launch.soon_notification_sent = False
        rocket_launch.liftoff_notification_sent = False
        rocket_launch.botched_launch = True
        await rocket_launch.save()
        LOGGER.warning(f"ROCKET Detected a status change to hold after it was set to {old_status} from {rocket_launch.name} ({rocket_launch.id})")
        embed = rocket_launch.generate_hold_embed()
    elif new_status in ["tbc", "tbd"]:
        rocket_launch.today_notification_sent = False
        rocket_launch.soon_notification_sent = False
        rocket_launch.liftoff_notification_sent = False
        rocket_launch.botched_launch = True
        await rocket_launch.save()
        LOGGER.warning(f"ROCKET Detected a status change to {new_status} after it was set to {old_status} from {rocket_launch.name} ({rocket_launch.id})")
        embed = rocket_launch.generate_tbc_embed()
    elif new_status == "go":
        rocket_launch.today_notification_sent = False
        rocket_launch.soon_notification_sent = False
        rocket_launch.liftoff_notification_sent = False
        rocket_launch.botched_launch = False
        await rocket_launch.save()
        LOGGER.warning(f"ROCKET Detected a status change to go after it was set to {old_status} from {rocket_launch.name} ({rocket_launch.id})")
        embed = rocket_launch.generate_go_embed()
    if not embed:
        return
    
    message = f"<@&{CONFIG.SPACE_NEWS_ROLE_ID}>"
    await send_in_channel(bot=bot, channel_id=CONFIG.SPACE_CHANNEL_ID, content=message, embed=embed)