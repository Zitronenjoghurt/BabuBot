import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.items.item_library import ItemLibrary
from src.items.types import Bait
from src.fishing.fish_library import FishEntry, FishLibrary
from src.logging.logger import LOGGER

CONFIG = Config.get_instance()
FISH_LIBRARY = FishLibrary.get_instance()
ITEM_LIBRARY = ItemLibrary.get_instance()

AVAILABLE_BAIT = ITEM_LIBRARY.get_available_bait()

class FishingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="fish", description="Fish for some random fish of random rarity!")
    @app_commands.describe(bait="The bait you want to use for fishing")
    async def fish(self, interaction: discord.Interaction, bait: Optional[str] = None):
        user: User = await User.load(userid=str(interaction.user.id))
        if not user.fishing.unlocked:
            return await interaction.response.send_message(embed=ErrorEmbed(title="YOU HAVE NO FISHING ROD", message="Look in the shop at `/shop rods` or buy the regular rod directly via `/buy R1` or `/buy Regular Rod` to get going!"), ephemeral=True)
        
        if bait and bait not in AVAILABLE_BAIT:
            return await interaction.response.send_message(embed=ErrorEmbed(title="BAIT DOES NOT EXIST", message=f"The bait {bait} you provided does not exist.\nCheck `/shop bait` or `/inventory bait`."), ephemeral=True)

        rod_level = user.fishing.rod_level
        bait_level = 0
        if bait:
            bait_item = ITEM_LIBRARY.find(identifier=bait)
            if isinstance(bait_item, Bait):
                if not user.inventory.has_item(bait_item.id):
                    return await interaction.response.send_message(embed=ErrorEmbed(title="YOU DONT OWN THAT BAIT", message=f"You currently dont own `{bait}`.\nYou can see your available bait with `/inventory bait`."), ephemeral=True)
                bait_level = bait_item.bait_level
            else:
                return await interaction.response.send_message(embed=ErrorEmbed(title="ERROR", message=f"An error occured while retrieving the bait item {bait}, please contact the developer."), ephemeral=True)

        fish_entry = FISH_LIBRARY.random_fish_entry(rod_level=rod_level, bait_level=bait_level)
        if not isinstance(fish_entry, FishEntry):
            LOGGER.error(f"Unable to retrieve random fish entry, received: {fish_entry}")
            return await interaction.response.send_message(embed=ErrorEmbed(title="AN ERROR OCCURED", message="An error occured while selecting a random fish, please contact the developer."), ephemeral=True)
        
        size = fish_entry.get_random_size()
        size_str = f"{round(size, 2)}cm ({fish_entry.size_classification(size=size)})"
        first_catch, record_size = user.fishing.process_fish(fish_entry=fish_entry, size=size)
        await user.save()

        if first_catch:
            await send_first_catch_embed(interaction=interaction, fish_entry=fish_entry, size=size_str)
        else:
            total_count = user.fishing.get_total_count(fish_entry.id)
            current_count = user.fishing.get_current_count(fish_entry.id)
            await send_catch_embed(interaction=interaction, fish_entry=fish_entry, size=size_str, record_size=record_size, current=current_count, total=total_count)

    @fish.autocomplete("bait")
    async def shop_category_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=category_choice, value=category_choice)
            for category_choice in AVAILABLE_BAIT
            if current.lower() in category_choice.lower()
        ]

async def send_first_catch_embed(interaction: discord.Interaction, fish_entry: FishEntry, size: str) -> None:
    embed = discord.Embed(
        title=f"{fish_entry.rarity.name} CATCH",
        description=f"You have caught {fish_entry.get_emoji()} **`{fish_entry.name}`** for the first time!\nSize: `{size}`",
        color=discord.Color.from_str(fish_entry.get_rarity_color()),
        timestamp=datetime.now()
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.add_field(name="Description", value=f"*{fish_entry.description}*", inline=False)
    embed.add_field(name="Price", value=f"**`{fish_entry.price}{CONFIG.CURRENCY}`**")
    embed.add_field(name="Type", value=f"**`{fish_entry.type.name.capitalize()}`**")

    file = discord.File(fish_entry.get_image_path(), filename=fish_entry.get_image_file_name())
    embed.set_image(url=fish_entry.get_image_url())
    await interaction.response.send_message(embed=embed, file=file)

async def send_catch_embed(interaction: discord.Interaction, fish_entry: FishEntry, size: str, record_size: bool, current: int, total: int) -> None:
    embed = discord.Embed(
        title=f"{fish_entry.rarity.name} CATCH",
        description=f"You have caught {fish_entry.get_emoji()} **`{fish_entry.name}`**!",
        color=discord.Color.from_str(fish_entry.color)
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

    size_str = f"**`{size}`**"
    if record_size:
        size_str += "\n**NEW RECORD!**"
    embed.add_field(name="Size", value=size_str)
    embed.add_field(name="In Inventory", value=f"**`{current}`**")
    embed.add_field(name="Caught Total", value=f"**`{total}`**")

    await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(FishingCommands(bot))