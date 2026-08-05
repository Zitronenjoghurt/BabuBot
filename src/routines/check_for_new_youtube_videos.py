from discord.ext import commands
from src.apis.youtube_api import YoutubeApi
from src.constants.config import Config
from src.logging.logger import LOGGER
from src.utils.bot_operations import send_in_channel

ACTIVE = False
INTERVAL_SECONDS = 900

CONFIG = Config.get_instance()
#YT_API = YoutubeApi.get_instance()

async def run(bot: commands.Bot):
    pass
    #new_videos = await YT_API.get_new_youtube_videos()
    #for video in new_videos:
    #    message = f"<@&{CONFIG.YOUTUBE_NEWS_ROLE_ID}> from Clara's recommendations:\n**{video.channel_name}** uploaded an interesting new video!"
    #    embed = video.create_embed()
    #    success = await send_in_channel(bot=bot, channel_id=CONFIG.YOUTUBE_NOTIFICATION_CHANNEL_ID, content=message, embed=embed)
    #    if not success:
    #        LOGGER.error(f"Failed to send notification about new video '{video.title}' from {video.channel_name}'")