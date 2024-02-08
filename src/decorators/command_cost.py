import discord
from functools import wraps
from src.constants.config import Config
from src.entities.user import User
from src.ui.confirm_view import ConfirmView

CONFIG = Config.get_instance()

def command_cost(amount: int, command_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            user: User = await User.load(userid=str(interaction.user.id))

            # If the user has not accepted the cost notice for the given command yet
            if not user.has_accepted_command_cost(command_name=command_name):
                confirm_view = ConfirmView(interaction.user.id, timeout=60)
                embed = generate_cost_notice_embed(cost=amount)
                await interaction.response.send_message( embed=embed, view=confirm_view, ephemeral=True)
                confirm_view.message = await interaction.original_response()
                timed_out = await confirm_view.wait()

                if timed_out:
                    edit_cost_notice_timeout(embed=embed)
                    return await interaction.edit_original_response(embed=embed)
                if not confirm_view.confirmed:
                    edit_cost_notice_cancelled(embed=embed)
                    return await interaction.edit_original_response(embed=embed)
                
                user.add_accepted_command_cost(command_name=command_name)
                await user.save()
                edit_cost_notice_confirmed(embed=embed)
                return await interaction.edit_original_response(embed=embed)
            
            if user.economy.currency >= amount:
                success = user.economy.remove_currency(amount=amount)
                if not success:
                    return await interaction.response.send_message(embed=generate_not_enoug_money_embed(cost=amount), ephemeral=True)
                await user.save()

                # Proceed with the original command
                await func(self, interaction, *args, **kwargs)

                # Send a followup stating how much money was withdrawn
                return await interaction.followup.send(content=f"**`{amount}{CONFIG.CURRENCY}`** were withdrawn.", ephemeral=True)
            else:
                # Notify the user of insufficient currency
                return await interaction.response.send_message(embed=generate_not_enoug_money_embed(cost=amount), ephemeral=True)

        return wrapper
    return decorator

async def refund(user: User, amount: int, interaction: discord.Interaction, reason: str):
    user.economy.add_currency(amount=amount)
    await user.save()
    await interaction.followup.send(f"<@{interaction.user.id}> **`{amount}{CONFIG.CURRENCY}`** were refunded.\nReason: `{reason}`", ephemeral=True)

def generate_not_enoug_money_embed(cost: int) -> discord.Embed:
    return discord.Embed(
        title="NOT ENOUGH MONEY",
        description=f"This command costs **`{cost}{CONFIG.CURRENCY}`**",
        color=discord.Color.red()
    )

def generate_cost_notice_embed(cost: int) -> discord.Embed:
    embed = discord.Embed(
        title="ACCEPT COMMAND COST",
        description=f"Attention! This command will always cost you **`{cost}{CONFIG.CURRENCY}`**.\nIf you confirm this notice you will not receive it for this command anymore.",
        color=discord.Color.yellow()
    )
    return embed.set_footer(text="This message will time out in 1 minute")

def edit_cost_notice_confirmed(embed: discord.Embed) -> None:
    embed.title = "COMMAND COSTS CONFIRMED"
    embed.description = "You can now use the command again."
    embed.color = discord.Color.green()
    embed.remove_footer()

def edit_cost_notice_cancelled(embed: discord.Embed) -> None:
    embed.title = "CANCELLED"
    embed.color = discord.Color.red()
    embed.remove_footer()

def edit_cost_notice_timeout(embed: discord.Embed) -> None:
    embed.title = "TIMED OUT"
    embed.color = discord.Color.darker_gray()
    embed.remove_footer()