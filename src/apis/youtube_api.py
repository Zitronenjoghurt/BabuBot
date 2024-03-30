import discord
import re
from datetime import datetime, timedelta
from typing import Optional
from googleapiclient.discovery import build
from src.apis.abstract_api_controller import AbstractApiController
from src.apis.rate_limiting import rate_limit
from src.constants.config import Config
from src.logging.logger import LOGGER

CONFIG = Config.get_instance()

# Find channel ID by going to yt channel page source > og:url
# Needs 2 quota per channel check
# Can check for 150 channels per hour
# 80 channels per 30 mins
# 40 channels per 15 mins
# 12 channels per 5 mins
CHANNEL_IDS = {
    "ambiguousamphibian": "UCSDiMahT5qDCjoWtzruztkw",
    "Astrum": "UC-9b7aDP6ZN0coj9-xFnrtw",
    "Ceave Gaming": "UCFXc5nAao6554AIXlN9KgwQ",
    "Ceave Perspective": "UCepgG8BiC4jlGTSZfYkpHiQ",
    "Code Bullet": "UC0e3QhIYukixgh5VVpKHH9Q",
    "Design Doc": "UCNOVwMpD-5A1xzcQGbIHNeA",
    "Fern": "UCODHrzPMGbNv67e84WDZhQQ",
    "FitMC": "UCHZ986wm_sJT6wntdDTIIcw",
    "Jasper": "UC5bN6XKHDCFt_wYAJmsP_Mg",
    "Kaze Emanuar": "UCuvSqzfO_LV_QzHdmEj84SQ",
    "Kurzgesagt - In a Nutshell": "UCsXVk37bltHxD1rDPwtNM8Q",
    "Lowest Percent": "UCxQrToVDBwHKuyIr47X04yA",
    "melodysheep": "UCR9sFzaG9Ia_kXJhfxtFMBA",
    "Nile Blue": "UC1D3yD4wlPMico0dss264XA",
    "Nile Red": "UCFhXFikryT4aFcLkLw2LBLA",
    "Razbuten": "UCfHmyqCntYHQ81ZukNu66rg",
    "SEA": "UCG9ShGbASoiwHwFcLcAh9EA",
    "SmallAnt": "UC0VVYtw21rg2cokUystu2Dw",
    "The Science Asylum": "UCXgNowiGxwwnLeQ7DXTwXPg",
    "The Spiffing Brit": "UCRHXUZ0BxbkU2MYZgsuFgkQ",
    "Tier Zoo": "UCHsRtomD4twRf5WVHHk-cMw",
    "Veritasium": "UCHnyfMqiRRG1u-2MsSQLbXA",
    "Vsauce": "UC6nSFpj9HTCZ5t-N3Rm3-HA",
    "Vsauce2": "UCqmugCqELzhIMNYnsjScXXw",
    "Wirtual": "UCt-HTfaCUz8QIoknqyXKYiw",
    "Yosh": "UCh1zLfuN6F_X4eoNKCsyICA",
    "Zeltik": "UCudx6plmpbs5WtWvsvu-EdQ"
}

CHANNEL_COLORS = {
    "ambiguousamphibian": "#B0A02A",
    "Astrum": "#002863",
    "Ceave Gaming": "#EEEEEE",
    "Ceave Perspective": "#5A6DB9",
    "Code Bullet": "#12920B",
    "Design Doc": "#0B4B7B",
    "Fern": "#04FF49",
    "FitMC": "#E4AA7A",
    "Jasper": "#FFDD25",
    "Kaze Emanuar": "#82A155",
    "Kurzgesagt - In a Nutshell": "#208BD7",
    "Lowest Percent": "#016DE1",
    "melodysheep": "#1B1915",
    "Nile Blue": "#0062FD",
    "Nile Red": "#ED5107",
    "Razbuten": "#BCA28B",
    "SEA": "#1B0949",
    "SmallAnt": "#62354E",
    "The Science Asylum": "#3E7AB4",
    "The Spiffing Brit": "#3E83C7",
    "Tier Zoo": "#A3A8CD",
    "Veritasium": "#2674E8",
    "Vsauce": "#03BF02",
    "Vsauce2": "#126B9D",
    "Wirtual": "#C02223",
    "Yosh": "#A20E0A",
    "Zeltik": "#FD6200"
}

# Can use ~400 quota per hour
# https://developers.google.com/youtube/v3/determine_quota_cost
class YoutubeApi(AbstractApiController):
    _instance = None
    CALLS = 300
    SECONDS = 3600

    def __init__(self) -> None:
        if YoutubeApi._instance is not None:
            raise RuntimeError("Tried to initialize multiple instances of YoutubeApi.")
        super().__init__()
        self.api = build('youtube', 'v3', developerKey=CONFIG.YOUTUBE_API_KEY)
        self.last_videos: dict[str, YoutubeVideo] = {}
        self.upload_playlist_ids: dict[str, str] = {}
        self.avatar_urls: dict[str, str] = {}

    @staticmethod
    def get_instance() -> 'YoutubeApi':
        if YoutubeApi._instance is None:
            YoutubeApi._instance = YoutubeApi()
        return YoutubeApi._instance
    
    @rate_limit(calls=40, seconds=900)
    async def get_new_youtube_videos(self) -> list['YoutubeVideo']:
        new_videos = []
        for channel_name in CHANNEL_IDS.keys():
            # Cache channel avatar url and upload playlist id
            await self.update_avatar_url(channel_name=channel_name)
            await self.update_upload_playlist_id(channel_name=channel_name)

            video = await self.fetch_latest_video(channel_name=channel_name)
            if not isinstance(video, YoutubeVideo):
                LOGGER.error(f"YOUTUBE Unable to update latest video information of channel {channel_name}: Failed to fetch latest video.")
                continue

            new = self.update_video(channel_name=channel_name, video=video)
            if new:
                new_videos.append(video)

        return new_videos

    def update_video(self, channel_name: str, video: 'YoutubeVideo') -> bool:
        last_video = self.last_videos.get(channel_name, None)
        if last_video is None:
            LOGGER.debug(f"YOUTUBE initialized recent video for channel {channel_name}: '{video.title}'")
            self.last_videos[channel_name] = video
            return False
        
        if last_video.id == video.id:
            LOGGER.debug(f"YOUTUBE checked channel {channel_name}: no new video found")
            return False
        else:
            LOGGER.debug(f"YOUTUBE found new video for channel {channel_name}: '{video.title}'")
            self.last_videos[channel_name] = video
            return True
        
    async def update_avatar_url(self, channel_name: str) -> None:
        if channel_name in self.avatar_urls:
            return
        
        url = await self.fetch_channel_avatar_url(channel_name=channel_name)
        if isinstance(url, str):
            self.avatar_urls[channel_name] = url
        else:
            LOGGER.error(f"YOUTUBE Unable to update avatar url of channel {channel_name}: Failed to fetch avatar url")

    async def update_upload_playlist_id(self, channel_name: str) -> None:
        if channel_name in self.upload_playlist_ids:
            return
        
        id = await self.fetch_upload_playlist_id(channel_name=channel_name)
        if isinstance(id, str):
            self.upload_playlist_ids[channel_name] = id
        else:
            LOGGER.error(f"YOUTUBE Unable to update upload playlist id of channel {channel_name}: Failed to fetch upload playlist id.")
    
    @rate_limit(class_scope=True)
    async def fetch_channel_avatar_url(self, channel_name: str) -> Optional[str]:
        channel_id = CHANNEL_IDS.get(channel_name, None)
        if not channel_id:
            LOGGER.error(f"YOUTUBE An error occured while fetching avatar url of channel {channel_name}: invalid channel_id '{channel_id}'")
            return None
        
        channel_response = self.api.channels().list(
            id=channel_id,
            part='snippet'
        ).execute()

        items = channel_response.get('items', None)
        if not items or len(items) == 0:
            LOGGER.error(f"YOUTUBE An error occured while fetching avatar url of channel {channel_name}: channel_response did not yield any items\n{channel_response}")
            return None
        
        item = items[0]
        snippet = item.get('snippet', None)
        if not snippet:
            LOGGER.error(f"YOUTUBE An error occured while fetching avatar url of channel {channel_name}: channel_response.items did not yield any snippet\n{channel_response}")
            return None
        
        thumbnails = snippet.get('thumbnails', None)
        if not thumbnails:
            LOGGER.error(f"YOUTUBE An error occured while fetching avatar url of channel {channel_name}: channel_response.items.snippet did not yield any thumbnails\n{channel_response}")
            return None
        
        thumbnail = thumbnails.get("high", None)
        if not thumbnail:
            thumbnail = thumbnails.get("medium", None)
        if not thumbnail:
            thumbnail = thumbnails.get("default", None)
        if not thumbnail:
            LOGGER.error(f"YOUTUBE An error occured while fetching avatar url of channel {channel_name}: channel_response.items.snippet.thumbnails did not yield any high, medium or default thumbnail\n{channel_response}")
            return None
        
        url = thumbnail.get("url", None)
        if not url:
            LOGGER.error(f"YOUTUBE An error occured while fetching avatar url of channel {channel_name}: channel_response.items.snippet.thumbnails.thumbnail did not yield any url\n{channel_response}")
            return None
        
        return url
    
    @rate_limit(class_scope=True)
    async def fetch_upload_playlist_id(self, channel_name: str) -> Optional[str]:
        channel_id = CHANNEL_IDS.get(channel_name, None)
        if not channel_id:
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: invalid channel_id '{channel_id}'")
            return None
        
        # Costs 1 quota
        channel_response = self.api.channels().list(
            id=channel_id,
            part='contentDetails'
        ).execute()

        if not channel_response.get('items'):
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: channel response did not yield any items\n{channel_response}")
            return None

        try:
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        except Exception:
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: channel response did not yield any upload playlists\n{channel_response}")
            return None
        
        return uploads_playlist_id

    @rate_limit(class_scope=True)
    async def fetch_latest_video(self, channel_name: str) -> Optional['YoutubeVideo']:
        channel_id = CHANNEL_IDS.get(channel_name, None)
        if not channel_id:
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: invalid channel_id '{channel_id}'")
            return None
        
        upload_playlist_id = self.upload_playlist_ids.get(channel_name, None)
        if not isinstance(upload_playlist_id, str):
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: No upload playlist id in cache")
            return None
        
        # Costs 1 quota
        playlist_response = self.api.playlistItems().list(
            playlistId=upload_playlist_id,
            part='snippet',
            maxResults=1
        ).execute()

        items = playlist_response.get('items', None)
        if not items or len(items) == 0:
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: playlist_response did not yield any items\n{playlist_response}")
            return None

        item = items[0]
        snippet = item.get('snippet', None)
        if not snippet:
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: playlist_response.item did not yield a snippet\n{playlist_response}")
            return None
        resource_id = snippet.get('resourceId', None)
        if not resource_id:
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: playlist_response.item.snippet did not yield a resourceId\n{playlist_response}")
            return None

        video_id = resource_id.get('videoId')
        if not video_id:
            LOGGER.error(f"YOUTUBE An error occured while fetching last video of channel {channel_name}: playlist_response.item.snippet.resourceId did not yield a videoId\n{playlist_response}")
            return None
        
        title = snippet.get('title', None)
        published_at = snippet.get('publishedAt', None)
        avatar_url = self.avatar_urls.get(channel_name, None)

        length = await self.fetch_video_length(video_id=video_id)

        video = YoutubeVideo(
            id=video_id,
            channel_name=channel_name,
            channel_id=channel_id,
            title=title,
            date=published_at,
            length=length,
            avatar_url=avatar_url
        )

        return video

    @rate_limit(class_scope=True)
    async def fetch_video_length(self, video_id: str) -> Optional[timedelta]:
        # Costs 1 quota
        request = self.api.videos().list(
            part='contentDetails',
            id=video_id
        )
        response = request.execute()
        if response['items']:
            duration = response['items'][0]['contentDetails']['duration']
            pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
            match = pattern.match(duration)
            if not match:
                return None
            hours, minutes, seconds = (int(part) if part else 0 for part in match.groups())
            return timedelta(hours=float(hours), minutes=float(minutes), seconds=float(seconds))

class YoutubeVideo():
    def __init__(self, id: str, channel_name: str, channel_id: str, title: Optional[str], date: Optional[str], length: Optional[timedelta], avatar_url: Optional[str]) -> None:
        self.id = id
        self.channel_name = channel_name
        self.channel_id = channel_id
        self.title = title
        self.length = length
        self.avatar_url = avatar_url

        if isinstance(date, str):
            self.date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        else:
            self.date = None

    def get_thumbnail_url(self) -> str:
        return f"https://img.youtube.com/vi/{self.id}/maxresdefault.jpg"
    
    def get_video_url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.id}"
    
    def get_channel_url(self) -> str:
        return f"https://www.youtube.com/channel/{self.channel_id}"
    
    def get_channel_color(self) -> str:
        return CHANNEL_COLORS.get(self.channel_name, "#FF0000")

    def create_embed(self) -> discord.Embed:
        video_url = self.get_video_url()
        thumbnail_url = self.get_thumbnail_url()
        channel_url = self.get_channel_url()
        channel_color = self.get_channel_color()

        embed = discord.Embed(
            title=self.title,
            url=video_url,
            description=f"Watch the video [here]({video_url})",
            color=discord.Color.from_str(channel_color)
        )
        embed.set_author(name=self.channel_name, icon_url=self.avatar_url, url=channel_url)
        embed.set_image(url=thumbnail_url)
        if isinstance(self.date, datetime):
            embed.timestamp = self.date
        if isinstance(self.length, timedelta):
            embed.set_footer(text=f"Length: {str(self.length)}")

        return embed