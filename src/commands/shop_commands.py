import discord
from discord import app_commands
from discord.ext import commands
from src.items.item_library import ItemLibrary
from src.scrollables.shop_scrollable import ShopScrollable
from src.ui.scrollable_embed import ScrollableEmbed
from src.utils.interaction_operations import send_scrollable

ITEM_LIBRARY = ItemLibrary.get_instance()
SHOP_CATEGORIES = ITEM_LIBRARY.get_categories()

class ShopCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="shop", description="Look up available items for sale")
    @app_commands.describe(category="The category of items you want to look at")
    async def shop(self, interaction: discord.Interaction, category: str):
        items = ITEM_LIBRARY.get_items_by_category(category=category)
        scrollable = await ShopScrollable.create(items=items)

        embed = ScrollableEmbed(
            scrollable=scrollable,
            title=f"{category.upper()} SHOP",
            color=discord.Color.yellow()
        )
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)

    @shop.autocomplete("category")
    async def shop_category_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=category_choice, value=category_choice)
            for category_choice in SHOP_CATEGORIES
            if current.lower() in category_choice.lower()
        ]

async def setup(bot: commands.Bot):
    await bot.add_cog(ShopCommands(bot))