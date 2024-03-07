from discord.ext import commands
from src.entities.rocket_launch import RocketLaunch

ACTIVE = False
INTERVAL_SECONDS = 180

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
    pass

async def notify_launch_soon(bot: commands.Bot, launch: RocketLaunch):
    pass

async def notify_launch_liftoff_status(bot: commands.Bot, launch: RocketLaunch):
    pass