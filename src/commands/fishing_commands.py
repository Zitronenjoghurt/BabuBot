import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.entities.fishing import FISHING_COOLDOWN
from src.items.item_library import ItemLibrary
from src.items.types import Bait
from src.fishing.fish_library import FishEntry, FishLibrary
from src.logging.logger import LOGGER
from src.scrollables.fish_basket_scrollable import FishBasketScrollable
from src.scrollables.fish_dex_scrollable import FishDexScrollable
from src.scrollables.fish_sold_toplist_scrollable import FishSoldToplistScrollable
from src.scrollables.money_earned_toplist_scrollable import MoneyEarnedToplistScrollable
from src.scrollables.prestige_points_toplist_scrollable import PrestigePointsToplistScrollable
from src.ui.scrollable_embed import ScrollableEmbed
from src.utils.discord_time import relative_time, long_date_time
from src.utils.interaction_operations import send_scrollable

CONFIG = Config.get_instance()
FISH_LIBRARY = FishLibrary.get_instance()
ITEM_LIBRARY = ItemLibrary.get_instance()

AVAILABLE_BAIT = ITEM_LIBRARY.get_available_bait()
AVAILABLE_RARITIES = ["Common", "Uncommon", "Rare", "Legendary", "Mythical", "Godly"]
TOPLISTS = ["Prestige Points", "Money Earned", "Fish Sold"]

class FishingCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="fish", description="Fish for some random fish of random rarity!")
    @app_commands.describe(bait="The bait you want to use for fishing")
    @app_commands.checks.cooldown(1, 5)
    async def fish(self, interaction: discord.Interaction, bait: Optional[str] = None):
        user: User = await User.load(userid=str(interaction.user.id))
        if not user.fishing.unlocked:
            return await interaction.response.send_message(embed=ErrorEmbed(title="YOU HAVE NO FISHING ROD", message="Look in the shop at `/shop rods` or buy the regular rod directly via `/buy R1` or `/buy Regular Rod` to get going!"), ephemeral=True)
        
        if not user.fishing.can_fish():
            return await interaction.response.send_message(content=f"You can fish again {relative_time(int(user.fishing.next_fishing_stamp))}", ephemeral=True)

        if bait and bait not in AVAILABLE_BAIT:
            return await interaction.response.send_message(embed=ErrorEmbed(title="BAIT DOES NOT EXIST", message=f"The bait {bait} you provided does not exist.\nCheck `/shop bait` or `/inventory bait`."), ephemeral=True)

        rod_level = user.fishing.rod_level
        bait_level = 0
        bait_item = None
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
        
        if bait_item:
            user.inventory.consume_item(id=bait_item.id)
        await user.save()

        if first_catch:
            LOGGER.debug(f"FISH: User {interaction.user.name} ({interaction.user.id}) has caught fish '{fish_entry.id}' for the first time")
            await send_first_catch_embed(interaction=interaction, fish_entry=fish_entry, size=size_str)
        else:
            total_count = user.fishing.get_total_count(fish_entry.id)
            current_count = user.fishing.get_current_count(fish_entry.id)
            LOGGER.debug(f"FISH: User {interaction.user.name} ({interaction.user.id}) has caught fish '{fish_entry.id}'")
            await send_catch_embed(interaction=interaction, fish_entry=fish_entry, size=size_str, record_size=record_size, current=current_count, total=total_count)

        if user.fishing.notify_on_fishing_ready:
            asyncio.create_task(user.notify(
                bot=self.bot, 
                channel_id=CONFIG.FISHING_CHANNEL_ID, 
                try_dm=user.fishing.notify_dm,
                delay_seconds=FISHING_COOLDOWN,
                content="You can fish again :)"
            ))

    @fish.autocomplete("bait")
    async def fish_bait_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=category_choice, value=category_choice)
            for category_choice in AVAILABLE_BAIT
            if current.lower() in category_choice.lower()
        ]
    
    @app_commands.command(name="fish-basket", description="Shows you the fish you currently have in your basket")
    @app_commands.describe(member="The user you want to check the basket of")
    @app_commands.checks.cooldown(1, 5)
    async def fish_basket(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if member:
            if member.bot:
                return await interaction.response.send_message(embed=ErrorEmbed(title=f"ERROR", message="Bots do not fish."))
            target = member
            userid = str(member.id)
        else:
            target = interaction.user
            userid = str(interaction.user.id)

        user: User = await User.load(userid=userid)
        fishes = user.fishing.get_fishes_with_count_and_prestige()
        scrollable = await FishBasketScrollable.create(fishes=fishes)

        embed = ScrollableEmbed(
            scrollable=scrollable,
            title="FISH BASKET",
            color=target.color
        )
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)

    @app_commands.command(name="fish-sell", description="Sell the fish in your basket")
    async def fish_sell(self, interaction: discord.Interaction):
        user: User = await User.load(userid=str(interaction.user.id))

        amount, money = user.fishing.get_fish_sell_amount_and_money()
        if amount == 0:
            return await interaction.response.send_message(embed=ErrorEmbed(title="NO FISH", message="You currently have no fish to sell!\nUse `/fish` to catch some."), ephemeral=True)

        user.economy.add_currency(amount=money)
        user.fishing.sell_all()
        await user.save()
        LOGGER.debug(f"FISH: User {interaction.user.display_name} ({interaction.user.id}) has sold {amount} fish for {money}")

        embed = discord.Embed(
            title="FISH SOLD",
            description=f"You have sold **`{amount}`** fish for **`{money}{CONFIG.CURRENCY}`**!",
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

        fish_sold = user.fishing.get_fish_sold(fish_id=fish_entry.id)
        prestige_price = FISH_LIBRARY.calculate_fish_price(fish_entry.id, fish_sold)
        prestige_level = FISH_LIBRARY.get_prestige_level(fish_sold)
        prestige_bonus = FISH_LIBRARY.get_prestige_bonus(fish_sold)
        prestige_str = f"**`{prestige_price}{CONFIG.CURRENCY}`**\n**`Lvl {prestige_level} +{prestige_bonus*100}%`**"

        embed.add_field(name="Price", value=f"**`{fish_entry.price}{CONFIG.CURRENCY}`**")
        embed.add_field(name="Prestige Price", value=prestige_str)
        embed.add_field(name="Type", value=f"**`{fish_entry.type.name.capitalize()}`**")
        embed.add_field(name="Rarity", value=f"**`{fish_entry.rarity.name.capitalize()}`**")
        embed.add_field(name="Size Range", value=f"**`{fish_entry.get_size_range()}`**")
        embed.add_field(name="Caught Total", value=f"**`{user.fishing.get_total_count(fish_entry.id)}`**")
        embed.add_field(name="In Basket", value=f"**`{user.fishing.get_current_count(fish_entry.id)}`**")
        embed.add_field(name="Smallest Catch", value=f"**`{smallest}`**")
        embed.add_field(name="Biggest Catch", value=f"**`{biggest}`**")
        embed.add_field(name="Last Caught", value=f"{relative_time(int(user.fishing.get_last_catch_stamp(fish_entry.id)))}")
        embed.add_field(name="First Caught", value=f"{long_date_time(int(user.fishing.get_first_catch_stamp(fish_entry.id)))}")

        file = discord.File(fish_entry.get_image_path(), filename=fish_entry.get_image_file_name())
        embed.set_image(url=fish_entry.get_image_url())
        await interaction.response.send_message(embed=embed, file=file)

    @app_commands.command(name="fish-dex", description="Provides information about caught fish and which are still left")
    @app_commands.describe(rarity="The rarity of fish you want to look at")
    @app_commands.checks.cooldown(1, 5)
    async def fish_dex(self, interaction: discord.Interaction, rarity: Optional[str] = None):
        if rarity and rarity.capitalize() not in AVAILABLE_RARITIES:
            return await interaction.response.send_message(embed=ErrorEmbed(title="INVALID CATEGORY", message="The specified category does not exist."), ephemeral=True)

        user: User = await User.load(userid=str(interaction.user.id))

        fish_dex = user.fishing.get_fish_dex(rarity=rarity)
        scrollable = await FishDexScrollable.create(fish_dex=fish_dex)

        title = "FISH DEX"
        if rarity:
            title += f" ({rarity.upper()})"

        embed = ScrollableEmbed(
            scrollable=scrollable,
            title=title,
            color=interaction.user.color
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)

    @app_commands.command(name="fish-stats", description="Shows your overall stats about the fishing game")
    @app_commands.describe(member="The user you want to check the stats of")
    async def fish_stats(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if member:
            if member.bot:
                return await interaction.response.send_message(embed=ErrorEmbed(title=f"ERROR", message="Bots do not fish."))
            target = member
            userid = str(member.id)
        else:
            target = interaction.user
            userid = str(interaction.user.id)

        user: User = await User.load(userid=userid)
        if not user.fishing.unlocked:
            return await interaction.response.send_message(embed=ErrorEmbed(title="NOT PARTICIPATING", message="The specified user did not start fishing yet, maybe you want to help them get into the game c:"), ephemeral=True)
        
        start_stamp = int(user.fishing.started_at)
        total_count = user.fishing.get_total_fish_count()
        basket_count = user.fishing.get_basket_fish_count()
        cumulative_money = user.fishing.get_cumulative_money()
        dex_stats = user.fishing.get_fish_dex_stats()
        prestige_stats = user.fishing.get_prestige_stats()

        embed = discord.Embed(
            title="FISHING STATS",
            color=discord.Color.from_str("#FFFFFF"),
            timestamp=datetime.now()
        )
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        embed.add_field(name="Started At", value=f"{long_date_time(start_stamp)}\n{relative_time(start_stamp)}", inline=False)
        embed.add_field(name="Total Caught", value=f"**`{total_count}`**")
        embed.add_field(name="In Basket", value=f"**`{basket_count}`**")
        embed.add_field(name="Money Earned", value=f"**`{cumulative_money}{CONFIG.CURRENCY}`**")
        embed.add_field(name="Dex", value=dex_stats)
        embed.add_field(name="Prestige", value=prestige_stats)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fish-settings", description="Adjust various settings for the fishing game")
    @app_commands.describe(leave_one="If you always want to leave one fish in your basket when selling")
    @app_commands.describe(notify_fish_ready="If you want to get notified when you can fish again")
    @app_commands.describe(notify_dm="If you want to receive notifications via DM")
    async def fish_settings(self, interaction: discord.Interaction, leave_one: Optional[bool] = None, notify_fish_ready: Optional[bool] = None, notify_dm: Optional[bool] = None):
        user: User = await User.load(userid=str(interaction.user.id))

        adjusted_settings = False

        if isinstance(leave_one, bool):
            adjusted_settings = True
            user.fishing.leave_one = leave_one
        if isinstance(notify_fish_ready, bool):
            adjusted_settings = True
            user.fishing.notify_on_fishing_ready = notify_fish_ready
        if isinstance(notify_dm, bool):
            adjusted_settings = True
            user.fishing.notify_dm = notify_dm

        await user.save()

        settings = [
            "Always leave one fish (each) in basket",
            "Get notified when you can fish again",
            "Get notifications via DM"
        ]
        states = [
            yes_no(user.fishing.leave_one),
            yes_no(user.fishing.notify_on_fishing_ready),
            yes_no(user.fishing.notify_dm)
        ]

        if not adjusted_settings:
            embed = discord.Embed(title="SETTINGS", color=discord.Color.light_grey())
        else:
            embed = discord.Embed(title="SETTINGS UPDATED", color=discord.Color.green())
        for setting, state in zip(settings, states):
            embed.add_field(name=setting, value=f"`{state}`", inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fish-toplist", description="Display different toplists")
    @app_commands.describe(category="The kind of toplist you want to look at")
    @app_commands.checks.cooldown(1, 5)
    async def fish_toplist(self, interaction: discord.Interaction, category: str):
        await interaction.response.defer()

        if category not in TOPLISTS:
            return await interaction.followup.send(embed=ErrorEmbed(title="INVALID CATEGORY", message="The category you have provided does not exist."))

        match category:
            case "Prestige Points":
                users: list[User] = await User.global_prestige_point_toplist()
                scrollable = await PrestigePointsToplistScrollable.create(users=users)
            case "Money Earned":
                users: list[User] = await User.global_fishing_money_earned_toplist()
                scrollable = await MoneyEarnedToplistScrollable.create(users=users)
            case "Fish Sold":
                users: list[User] = await User.global_fish_sold_toplist()
                scrollable = await FishSoldToplistScrollable.create(users=users)
            case _:
                return await interaction.followup.send(embed=ErrorEmbed(title="INVALID CATEGORY", message="The category you have provided does not exist."))
        
        embed = ScrollableEmbed(
            scrollable=scrollable,
            title=category,
            color=discord.Color.from_str("#FFFFFF")
        )
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed, followup=True)

    @app_commands.command(name="fish-prestige", description="Retrieve your prestige status of a fish")
    @app_commands.describe(fish="The fish you want to know the prestige status of")
    async def fish_prestige(self, interaction: discord.Interaction, fish: str):
        user: User = await User.load(userid=str(interaction.user.id))

        fish_entry = FISH_LIBRARY.find(fish)
        if not isinstance(fish_entry, FishEntry) or not user.fishing.has_caught(fish_entry.id):
            return await interaction.response.send_message(embed=ErrorEmbed(title="NO INFORMATION AVAILABLE", message=f"Either you did not catch `{fish}` yet, or it does not exist.\nUse `/fish-dex` to check that you made no typo."), ephemeral=True)
        
        fish_sold = user.fishing.get_fish_sold(fish_id=fish_entry.id)
        prestige_lvl = FISH_LIBRARY.get_prestige_level(fish_sold=fish_sold)

        embed = discord.Embed(
            title=f"{prestige_lvl}★ {fish_entry.name} {fish_entry.get_emoji()}",
            color=discord.Color.from_str(FISH_LIBRARY.get_prestige_color(prestige_lvl))
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="PROGRESS", value=user.fishing.get_prestige_progress(fish_entry.id), inline=False)
        embed.add_field(name="Base Price", value=f"**`{fish_entry.price}{CONFIG.CURRENCY}`**")
        embed.add_field(name="Bonus", value=f"**`+{FISH_LIBRARY.get_prestige_bonus(fish_sold=fish_sold)*100}%`**")
        embed.add_field(name="Current Price", value=f"**`{FISH_LIBRARY.calculate_fish_price(id=fish_entry.id, fish_sold=fish_sold)}{CONFIG.CURRENCY}`**")

        file = discord.File(FISH_LIBRARY.get_prestige_image_path(prestige_lvl), filename=FISH_LIBRARY.get_prestige_image_file_name(prestige_lvl))
        embed.set_image(url=FISH_LIBRARY.get_prestige_image_url(prestige_lvl))
        await interaction.response.send_message(file=file, embed=embed)
    
    @app_commands.command(name="prestige", description="Retrieve all important information about your overall prestige")
    @app_commands.describe(member="The user you want to check the prestige of")
    async def prestige(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        if member:
            if member.bot:
                return await interaction.response.send_message(embed=ErrorEmbed(title=f"ERROR", message="Bots do not fish."))
            target = member
            userid = str(member.id)
            self_target = False
        else:
            target = interaction.user
            userid = str(interaction.user.id)
            self_target = True

        user: User = await User.load(userid=userid)
        if not user.fishing.unlocked:
            if self_target:
                embed = ErrorEmbed(title="NO FISHER", message="You did not start your fishing journey yet! Try buying a fishing rod with `/buy item:R1` (you can get some money with `/daily`).")
            else:
                embed = ErrorEmbed(title="NO FISHER", message="The specified user did not start their fishing journey yet! Maybe help them get started c:")
            return await interaction.response.send_message(embed=embed)

        embed = discord.Embed(
            title="PRESTIGE",
            color=target.color
        )
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        embed.add_field(name="AVAILABLE POINTS", value=f"`{user.fishing.get_current_prestige_points()}🏅`", inline=False)
        embed.add_field(name="TOTAL POINTS EARNED", value=f"`{user.fishing.get_total_prestige_earned()}🏅`", inline=False)
        embed.add_field(name="TOTAL PROGRESS", value=f"**`{round(user.fishing.get_total_prestige_progress(), 4)}%`**", inline=False)
        await interaction.response.send_message(embed=embed)

    @fish_dex.autocomplete("rarity")
    async def fish_rarity(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=rarity, value=rarity)
            for rarity in AVAILABLE_RARITIES
            if current.lower() in rarity.lower()
        ]
    
    @fish_toplist.autocomplete("category")
    async def fish_toplist_category(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=category, value=category)
            for category in TOPLISTS
            if current.lower() in category.lower()
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

    if len(fish_entry.followup_content) > 0:
        await interaction.followup.send(content=fish_entry.followup_content)

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
    embed.add_field(name="In Basket", value=f"**`{current}`**")
    embed.add_field(name="Caught Total", value=f"**`{total}`**")

    await interaction.response.send_message(embed=embed)

def yes_no(state: bool) -> str:
    if state:
        return "Yes"
    return "No"

async def setup(bot):
    await bot.add_cog(FishingCommands(bot))