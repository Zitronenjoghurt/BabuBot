import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User
from src.items.item_library import ItemLibrary
from src.scrollables.inventory_scrollable import InventoryScrollable
from src.ui.scrollable_embed import ScrollableEmbed
from src.utils.interaction_operations import send_scrollable

CONFIG = Config.get_instance()
ITEM_LIBRARY = ItemLibrary.get_instance()
ITEM_CATEGORIES = ITEM_LIBRARY.get_categories()

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="item", description=f"Look up important information about a specified item")
    @app_commands.describe(item="The name/id of the item you want to look up")
    async def item(self, interaction: discord.Interaction, item: str):
        entry = ITEM_LIBRARY.find(identifier=item)
        if entry is None:
            return await interaction.response.send_message(embed=ErrorEmbed(title="ITEM NOT FOUND", message=f"Item **`{item}`** does not exist.\nUse `/shop` and check that you got the right name or id."), ephemeral=True)
        
        user: User = await User.load(userid=str(interaction.user.id))
        count = user.inventory.item_count(entry.id)

        embed = discord.Embed(
            title=entry.display_name.upper(),
            description=f"*{entry.description}*",
            color=discord.Color.from_str(entry.color)
        )
        embed.set_author(name=f"Category: {entry.category.upper()}")
        embed.add_field(name="Use", value=entry.use, inline=False)

        # Set requirements or inventory field depending on prerequisites
        if (entry.needs_item or entry.has_requirements()) and count == 0:
            requirements = entry.get_requirements()
            if entry.needs_item:
                required_item = ITEM_LIBRARY.get_item_by_id(id=entry.needs_item)
                if required_item:
                    requirements += f"\n- acquire **`{required_item.display_name}`**"
            embed.add_field(name="Requirements", value=requirements, inline=False)
        else:
            if count == 0:
                ownership = "❌ **`You don't own this item`**"
            elif count == 1:
                ownership = "✅ **`You OWN this item`**"
            else:
                ownership = f"✅ **`You have {count} of this.`**"
            embed.add_field(name="Inventory", value=ownership, inline=False)
        
        embed.add_field(name="Price", value=f"**`{entry.price}{CONFIG.CURRENCY}`**")
        embed.add_field(name="Item Cap", value=f"**`{entry.max_count}`**")
        embed.add_field(name="ID", value=f"**`{entry.id}`**")
        if count == 0:
            embed.set_footer(text=f"use /buy {entry.id} or /buy {entry.display_name}")

        file = discord.File(entry.get_image_path(), filename=entry.get_image_file_name())
        embed.set_image(url=entry.get_image_url())
        await interaction.response.send_message(file=file, embed=embed)

    @app_commands.command(name="inventory", description=f"Look up items you own")
    @app_commands.describe(category="The name/id of the items in your inventory you want to check")
    @app_commands.describe(member="The user you want to see the inventory of")
    @app_commands.checks.cooldown(1, 5)
    async def inventory(self, interaction: discord.Interaction, category: Optional[str] = None, member: Optional[discord.Member] = None):
        if category:
            category = category.lower()
        if category and category not in ITEM_CATEGORIES:
            categories = ", ".join(ITEM_CATEGORIES)
            return await interaction.response.send_message(embed=ErrorEmbed(title="CATEGORY NOT FOUND", message=f"Category **`{category}`** does not exist.\nAvailable categories are: {categories}."), ephemeral=True)

        if member:
            target = member
            userid = str(member.id)
        else:
            target = interaction.user
            userid = str(interaction.user.id)

        user: User = await User.load(userid=userid)
        items_mapped = user.inventory.map_items_by_id_and_count()

        items_with_count = ITEM_LIBRARY.items_with_count_from_id_with_count(data=items_mapped, category=category)
        scrollable = await InventoryScrollable.create(items_with_count=items_with_count)

        title = "INVENTORY"
        if category:
            title += f" ({category.upper()})"

        embed = ScrollableEmbed(
            scrollable=scrollable,
            title=title,
            color=target.color
        )
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)

    @inventory.autocomplete("category")
    async def shop_category_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=category_choice, value=category_choice)
            for category_choice in ITEM_CATEGORIES
            if current.lower() in category_choice.lower()
        ]

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))