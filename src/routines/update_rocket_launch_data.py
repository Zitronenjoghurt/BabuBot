from discord.ext import commands
from src.apis.launch_library2_api import LaunchLibrary2Api

ACTIVE = False
INTERVAL_SECONDS = 300

LL2 = LaunchLibrary2Api.get_instance()

async def run(bot: commands.Bot):
    updated_fields = await LL2.update_launches()