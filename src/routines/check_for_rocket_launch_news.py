from discord.ext import commands
from src.constants.config import Config
from src.entities.rocket_launch.rocket_launch import RocketLaunch
from src.logging.logger import LOGGER
from src.utils.bot_operations import send_in_channel

ACTIVE = False
INTERVAL_SECONDS = 180

CONFIG = Config.get_instance()

async def run(bot: commands.Bot):
    launches: list[RocketLaunch] = await RocketLaunch.findall(sort_key="net", descending=False)

    for launch in launches:
        send_notification = False
        embed = None
        if launch.notify_launching_today():
            embed = launch.generate_today_embed()
            launch.today_notification_sent = True
            send_notification = True
        elif launch.notify_launching_soon():
            embed = launch.generate_soon_embed()
            launch.soon_notification_sent = True
            send_notification = True
        elif launch.notify_liftoff_status():
            embed = launch.generate_liftoff_status_embed()
            launch.liftoff_notification_sent = True
            send_notification = True
        
        if send_notification and embed:
            await launch.save()
            message = f"<@&{CONFIG.SPACE_NEWS_ROLE_ID}>"
            await send_in_channel(bot=bot, channel_id=CONFIG.SPACE_CHANNEL_ID, content=message, embed=embed)

        if launch.should_remove_entry():
            await launch.delete()