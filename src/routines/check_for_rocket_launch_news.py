from discord.ext import commands
from src.constants.config import Config
from src.entities.rocket_launch import RocketLaunch
from src.logging.logger import LOGGER
from src.utils.bot_operations import send_in_channel

ACTIVE = True
INTERVAL_SECONDS = 180

CONFIG = Config.get_instance()

async def run(bot: commands.Bot):
    launches: list[RocketLaunch] = await RocketLaunch.findall(sort_key="net", descending=False)

    for launch in launches:
        if launch.notify_launching_today():
            await notify_launch_today(bot=bot, launch=launch)
            launch.notifications_sent = 1
        if launch.notify_launching_soon():
            await notify_launch_soon(bot=bot, launch=launch)
            launch.notifications_sent = 2
        if launch.notify_liftoff_status():
            await notify_launch_liftoff_status(bot=bot, launch=launch)
            launch.notifications_sent = 3
        
        await launch.save()
        if launch.should_remove_entry():
            await launch.delete()

async def notify_launch_today(bot: commands.Bot, launch: RocketLaunch):
    embed = launch.generate_today_embed()
    await send_in_channel(bot=bot, channel_id=CONFIG.SPACE_CHANNEL_ID, embed=embed)

async def notify_launch_soon(bot: commands.Bot, launch: RocketLaunch):
    embed = launch.generate_soon_embed()
    await send_in_channel(bot=bot, channel_id=CONFIG.SPACE_CHANNEL_ID, embed=embed)

async def notify_launch_liftoff_status(bot: commands.Bot, launch: RocketLaunch):
    embed = launch.generate_liftoff_status_embed()
    if not embed:
        LOGGER.warn(f"ROCKET Was unable to generate liftoff embed for launch {launch.name} ({launch.launch_id})")
        return
    await send_in_channel(bot=bot, channel_id=CONFIG.SPACE_CHANNEL_ID, embed=embed)