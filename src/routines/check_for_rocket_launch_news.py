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
        send_notification = False
        embed = None
        if launch.notify_launching_today():
            embed = launch.generate_today_embed()
            launch.notifications_sent = 1
            send_notification = True
        elif launch.notify_launching_soon():
            embed = launch.generate_soon_embed()
            launch.notifications_sent = 2
            send_notification = True
        elif launch.notify_liftoff_status():
            embed = launch.generate_liftoff_status_embed()
            launch.notifications_sent = 3
            send_notification = True
            if not embed:
                LOGGER.warn(f"ROCKET Was unable to generate liftoff status embed for launch {launch.name} ({launch.launch_id})")
        
        if send_notification and embed:
            await launch.save()
            message = f"<@&{CONFIG.SPACE_NEWS_ROLE_ID}>"
            await send_in_channel(bot=bot, channel_id=CONFIG.SPACE_CHANNEL_ID, content=message, embed=embed)

        if launch.should_remove_entry():
            await launch.delete()