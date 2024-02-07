import discord
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.config import Config
from src.constants.custom_embeds import ErrorEmbed
from src.entities.economy import STREAK_THRESHOLD_DAYS
from src.entities.user import User
from src.ui.confirm_view import ConfirmView
from src.utils.bot_operations import retrieve_guild_strict
from src.utils.discord_time import relative_time
from src.utils.guild_operations import retrieve_member_strict, retrieve_members

CONFIG = Config.get_instance()

class EconomyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="daily", description=f"Receive some daily {CONFIG.CURRENCY}")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        user: User = await User.load(userid=user_id)

        loses_streak = user.economy.will_lose_streak()
        last_daily_stamp = relative_time(int(user.economy.last_daily_stamp))
        success, amount = user.economy.do_daily()
        
        if not success:
            embed = ErrorEmbed(
                title="You already got your daily today!", 
                message=f"You can get your next daily {user.economy.next_daily_discord_stamp()}\nYour current streak is: **`{user.economy.daily_streak}`**"
            )
            await interaction.response.send_message(embed=embed)
            return
        
        await user.save()
        
        embed = discord.Embed(title="DAILY COLLECTED", description=f"You have received **`{amount}{CONFIG.CURRENCY}`**", color=discord.Color.from_str("#f2ad46"))
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        if loses_streak:
            embed.add_field(name="YOU LOST YOUR STREAK", value=f"Your last daily was {last_daily_stamp}. After {STREAK_THRESHOLD_DAYS} days of not collecting it you will lose your streak so be careful!", inline=False)
        embed.add_field(name="CURRENT STREAK", value=f"**`{user.economy.daily_streak}`**")
        embed.add_field(name="NEXT DAILY", value=user.economy.next_daily_discord_stamp())
        if not loses_streak:
            embed.set_footer(text=f"You lose your streak after {STREAK_THRESHOLD_DAYS} days of not collecting it again!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="money", description=f"Check the balance of yourself or the specified user")
    @app_commands.describe(member="The user you want to check the balance of")
    async def money(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        if isinstance(member, discord.Member):
            user_id = member.id
        else:
            user_id = interaction.user.id
            guild = await retrieve_guild_strict(self.bot, CONFIG.GUILD_ID)
            member = await retrieve_member_strict(guild=guild, member_id=user_id)

        user: User = await User.load(userid=str(user_id))
        
        embed = discord.Embed(title="MONEY", description=f"**`{user.economy.currency}{CONFIG.CURRENCY}`**", color=discord.Color.from_str("#f2ad46"))
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.add_field(name="DAILY STREAK", value=f"**`{user.economy.daily_streak}`**")
        embed.add_field(name="NEXT DAILY", value=user.economy.next_daily_discord_stamp())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="money-toplist", description=f"Display the people with the most {CONFIG.CURRENCY} on the server")
    async def money_toplist(self, interaction: discord.Interaction):
        await interaction.response.defer()
        toplist = await build_money_toplist(page=1)
        
        embed = discord.Embed(title="MONEY TOPLIST", description=toplist, color=discord.Color.from_str("#FFFFFF"))
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="money-give", description=f"Display the people with the most {CONFIG.CURRENCY} on the server")
    @app_commands.describe(member="The user you want to give mone")
    @app_commands.describe(member="The amount of money you want to give")
    @app_commands.checks.cooldown(5, 300)
    async def money_give(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount < 1:
            await interaction.response.send_message(embed=ErrorEmbed(title="Thats too little!", message=f"You have to send at least **`1{CONFIG.CURRENCY}`**!"))
            return
        
        user: User = await User.load(userid=str(interaction.user.id))
        if user.economy.currency < amount:
            await interaction.response.send_message(embed=ErrorEmbed(title="You don't have that much money...", message=f"You currently only have **`{user.economy.currency}{CONFIG.CURRENCY}`**!"))
            return
        
        confirm_embed = discord.Embed(
            title="CONFIRM TRANSACTION", 
            description=f"If you confirm this transaction, **`{amount}{CONFIG.CURRENCY}`** will be sent to **{member.display_name}**", 
            color=discord.Color.from_str("#f2ad46"), 
            timestamp=datetime.now()
        )
        confirm_embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        confirm_embed.set_footer(text="If you dont react within 3 minutes, this transaction will time out.")
        
        confirm_view = ConfirmView(user_id=interaction.user.id, timeout=5)
        await interaction.response.send_message(embed=confirm_embed, view=confirm_view)
        confirm_view.message = await interaction.original_response()
        timed_out = await confirm_view.wait()

        if confirm_view.confirmed:
            target: User = await User.load(userid=str(member.id))
            success = user.economy.send_money(amount, target.userid)
            if success:
                target.economy.receive_money(amount, user.userid)
                await user.save()
                await target.save()
                confirm_embed.title = "TRANSACTION SUCCESSFUL"
                confirm_embed.description = f"**{interaction.user.display_name}** sent **`{amount}{CONFIG.CURRENCY}`** to **{member.display_name}**!"
                confirm_embed.color = discord.Color.green()
            else:
                confirm_embed.title = "AN ERROR OCCURED"
                confirm_embed.color = discord.Color.red()
        elif timed_out:
            confirm_embed.title = "TRANSACTION TIMED OUT"
            confirm_embed.color = discord.Color.darker_grey()
        else:
            confirm_embed.title = "TRANSACTION CANCELLED"
            confirm_embed.color = discord.Color.red()
        confirm_embed.remove_footer()
        await interaction.edit_original_response(embed=confirm_embed)

    @money_give.error
    async def on_money_give_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        await interaction.response.send_message(embed=ErrorEmbed(title="ERROR", message=str(error)), ephemeral=True)

async def build_money_toplist(page: int = 1) -> str:
    users: list[User] = await User.findall(sort_key="economy.currency", limit=20, page=page)

    user_positions = []
    for i, user in enumerate(users):
        user_positions.append(f"#**{i+1}** ❥ **`{user.economy.currency}{CONFIG.CURRENCY}`** | **{user.get_display_name()}**")
    return "\n".join(user_positions)

async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCommands(bot))