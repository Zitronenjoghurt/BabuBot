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
from src.scrollables.fish_basket_scrollable import FishBasketScrollable
from src.scrollables.fish_dex_scrollable import FishDexScrollable
from src.ui.scrollable_embed import ScrollableEmbed
from src.utils.discord_time import relative_time, long_date_time
from src.utils.interaction_operations import send_scrollable

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
                    return await interaction.response.send_message(embed=ErrorEmbed(title="YOU DONT OWN THAT BAIT", message=f"You currently dont have `{bait}`.\nYou can see your available bait with `/inventory bait`."), ephemeral=True)
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
    
    @app_commands.command(name="fish-basket", description="Shows you the fish you currently have in your basket")
    @app_commands.describe(member="The user you want to check the basket of")
    async def fish_basket(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if member:
            target = member
            userid = str(member.id)
        else:
            target = interaction.user
            userid = str(interaction.user.id)

        user: User = await User.load(userid=userid)
        fishes = user.fishing.get_fishes_with_count()
        scrollable = await FishBasketScrollable.create(fishes=fishes)

        embed = ScrollableEmbed(
            scrollable=scrollable,
            title="FISH BASKET",
            color=target.color
        )
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)

    @app_commands.command(name="fish-sell", description="Sell all of the fish in your basket")
    async def fish_sell(self, interaction: discord.Interaction):
        user: User = await User.load(userid=str(interaction.user.id))

        fishes = user.fishing.get_fishes_with_count()
        if len(fishes) == 0:
            return await interaction.response.send_message(embed=ErrorEmbed(title="NO FISH", message="You currently have no fish to sell!\nUse `/fish` to catch some."), ephemeral=True)
        
        money = 0
        total_count = 0
        for fish_id, count in fishes:
            fish_entry = FISH_LIBRARY.get_by_id(fish_id)
            if not isinstance(fish_entry, FishEntry):
                continue
            money += fish_entry.price * count
            total_count += count

        user.economy.add_currency(amount=money)
        user.fishing.sell_all()
        await user.save()

        embed = discord.Embed(
            title="FISH SOLD",
            description=f"You have sold **`{total_count}`** fish for **`{money}{CONFIG.CURRENCY}`**!",
            color=discord.Color.yellow(),
            timestamp=datetime.now()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fish-info", description="Retrieve information about a fish")
    @app_commands.describe(fish="The fish you want to know more about")
    async def fish_info(self, interaction: discord.Interaction, fish: str):
        user: User = await User.load(userid=str(interaction.user.id))

        fish_entry = FISH_LIBRARY.find(fish)
        if not isinstance(fish_entry, FishEntry) or not user.fishing.has_caught(fish_entry.id):
            return await interaction.response.send_message(embed=ErrorEmbed(title="NO INFORMATION AVAILABLE", message=f"Either you did not catch `{fish}` yet, or it does not exist.\nUse `/fish-dex` to check that you made no typo."), ephemeral=True)

        embed = discord.Embed(
            title=f"{fish_entry.get_emoji()} {fish_entry.name} ({fish_entry.scientific})",
            description=f"*{fish_entry.description}*",
            color=discord.Color.from_str(fish_entry.color)
        )

        min_size = round(user.fishing.get_min_size(fish_entry.id), CONFIG.DECIMAL_DIGITS)
        max_size = round(user.fishing.get_max_size(fish_entry.id), CONFIG.DECIMAL_DIGITS)

        smallest = f"{min_size}cm ({fish_entry.size_classification(min_size)})"
        biggest = f"{max_size}cm ({fish_entry.size_classification(max_size)})"

        embed.add_field(name="Price", value=f"**`{fish_entry.price}{CONFIG.CURRENCY}`**")
        embed.add_field(name="Type", value=f"**`{fish_entry.type.name.capitalize()}`**")
        embed.add_field(name="Rarity", value=f"**`{fish_entry.rarity.name.capitalize()}`**")
        embed.add_field(name="Size Range", value=f"**`{fish_entry.get_size_range()}`**")
        embed.add_field(name="Caught Total", value=f"**`{user.fishing.get_total_count(fish_entry.id)}`**")
        embed.add_field(name="In Inventory", value=f"**`{user.fishing.get_current_count(fish_entry.id)}`**")
        embed.add_field(name="Smallest Caught", value=f"**`{smallest}`**")
        embed.add_field(name="Biggest Caught", value=f"**`{biggest}`**")
        embed.add_field(name="Last Caught", value=f"{relative_time(int(user.fishing.get_first_catch_stamp(fish_entry.id)))}")
        embed.add_field(name="First Caught", value=f"{long_date_time(int(user.fishing.get_first_catch_stamp(fish_entry.id)))}")

        file = discord.File(fish_entry.get_image_path(), filename=fish_entry.get_image_file_name())
        embed.set_image(url=fish_entry.get_image_url())
        await interaction.response.send_message(embed=embed, file=file)

    @app_commands.command(name="fish-dex", description="Provides information about caught fish and which are still left")
    async def fish_dex(self, interaction: discord.Interaction):
        user: User = await User.load(userid=str(interaction.user.id))

        caught_fish_ids = user.fishing.get_fishes()
        fish_dex = FISH_LIBRARY.generate_fish_dex(caught_ids=caught_fish_ids)

        scrollable = await FishDexScrollable.create(fish_dex=fish_dex)

        embed = ScrollableEmbed(
            scrollable=scrollable,
            title="FISH DEX",
            color=interaction.user.color
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)

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