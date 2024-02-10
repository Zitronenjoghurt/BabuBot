import discord
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.items.item_library import ItemLibrary
from src.scrollables.shop_scrollable import ShopScrollable
from src.ui.confirm_view import ConfirmView
from src.ui.scrollable_embed import ScrollableEmbed
from src.utils.interaction_operations import send_scrollable

CONFIG = Config.get_instance()

ITEM_LIBRARY = ItemLibrary.get_instance()
SHOP_CATEGORIES = ITEM_LIBRARY.get_categories()

class ShopCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="shop", description="Look up available items for sale")
    @app_commands.describe(category="The category of items you want to look at")
    @app_commands.checks.cooldown(1, 5)
    async def shop(self, interaction: discord.Interaction, category: str):
        if category not in SHOP_CATEGORIES:
            categories = ", ".join(SHOP_CATEGORIES)
            return await interaction.response.send_message(embed=ErrorEmbed(title="CATEGORY NOT FOUND", message=f"Category **`{category}`** does not exist.\nAvailable categories are: {categories}."), ephemeral=True)
        
        items = ITEM_LIBRARY.get_items_by_category(category=category)
        scrollable = await ShopScrollable.create(items=items)

        embed = ScrollableEmbed(
            scrollable=scrollable,
            title=f"{category.upper()} SHOP",
            color=discord.Color.yellow()
        )
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)

    @app_commands.command(name="buy", description="If you want to buy an item you saw in /shop")
    @app_commands.describe(item="The name/id of the item you want to buy")
    @app_commands.checks.cooldown(1, 5)
    async def buy(self, interaction: discord.Interaction, item: str, amount: Optional[int] = None):
        if amount is None or amount < 1:
            amount = 1

        buy_item = ITEM_LIBRARY.find(identifier=item)
        if buy_item is None:
            return await interaction.response.send_message(embed=ErrorEmbed(title="ITEM NOT FOUND", message=f"Item **`{item}`** does not exist.\nUse `/shop` and check that you got the right name or id."), ephemeral=True)

        user: User = await User.load(userid=str(interaction.user.id))

        can_buy, message = buy_item.can_buy(user=user, amount=amount)
        if not can_buy:
            return await interaction.response.send_message(embed=ErrorEmbed(title="ERROR", message=message), ephemeral=True)
        
        confirm_embed = discord.Embed(
            title="CONFIRM PURCHASE",
            description=f"Do you want to buy {buy_item.get_emoji()} **`{amount}x {buy_item.display_name}`**?\n\nIt will cost **`{buy_item.price*amount}{CONFIG.CURRENCY}`** and you currently have **`{user.economy.currency}{CONFIG.CURRENCY}`**",
            color=discord.Color.yellow(),
            timestamp=datetime.now()
        )
        confirm_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        
        confirm_view = ConfirmView(user_id=interaction.user.id)
        await interaction.response.send_message(embed=confirm_embed, view=confirm_view)
        confirm_view.message = await interaction.original_response()
        timed_out = await confirm_view.wait()

        if confirm_view.confirmed:
            # Reload user because in between they couldve already spent currency elsewhere
            user: User = await User.load(userid=str(interaction.user.id))
            success, message = await buy_item.buy(user=user, amount=amount)
            if success:
                await user.save()
                confirm_embed.title = "PURCHASE SUCCESSFUL!"
                confirm_embed.description = f"You successfully bought {buy_item.get_emoji()} **`{amount}x {buy_item.display_name}`**"
                confirm_embed.color = discord.Color.green()
                confirm_embed.set_footer(text="Check your inventory with /inventory")
            else:
                confirm_embed.title = "PURCHASE FAILED"
                confirm_embed.description = message
                confirm_embed.color = discord.Color.red()
        elif timed_out:
            confirm_embed.title = "PURCHASE TIMED OUT"
            confirm_embed.color = discord.Color.darker_grey()
        else:
            confirm_embed.title = "PURCHASE CANCELLED"
            confirm_embed.color = discord.Color.red()
        await interaction.edit_original_response(embed=confirm_embed)

    @shop.autocomplete("category")
    async def shop_category_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=category_choice, value=category_choice)
            for category_choice in SHOP_CATEGORIES
            if current.lower() in category_choice.lower()
        ]

async def setup(bot: commands.Bot):
    await bot.add_cog(ShopCommands(bot))