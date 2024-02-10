import discord
from discord import app_commands
from discord.ext import commands
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.items.item_library import ItemLibrary

CONFIG = Config.get_instance()
ITEM_LIBRARY = ItemLibrary.get_instance()

class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="item", description=f"Look up important information about a specified item")
    @app_commands.describe(item="The name/id of the item you want to look up")
    async def item(self, interaction: discord.Interaction, item: str):
        entry = ITEM_LIBRARY.find(identifier=item)
        if entry is None:
            return await interaction.response.send_message(embed=ErrorEmbed(title="ITEM NOT FOUND", message=f"Item **`{item}`** does not exist.\nUse `/shop` and check that you got the right name or id."), ephemeral=True)
        
        embed = discord.Embed(
            title=entry.display_name.upper(),
            description=f"*{entry.description}*",
            color=discord.Color.from_str(entry.color)
        )
        embed.set_author(name=f"Category: {entry.category.upper()}")
        embed.add_field(name="Use", value=entry.use, inline=False)
        embed.add_field(name="Price", value=f"**`{entry.price}{CONFIG.CURRENCY}`**")
        embed.add_field(name="Maximum Stack", value=f"**`{entry.max_count}`**")
        embed.add_field(name="ID", value=f"**`{entry.id}`**")
        embed.set_footer(text=f"use /buy {entry.id} or /buy {entry.display_name}")

        file = discord.File(entry.get_image_path(), filename=entry.get_image_file_name())
        embed.set_image(url=entry.get_image_url())
        await interaction.response.send_message(file=file, embed=embed)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))