import discord
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from src.constants.custom_embeds import ErrorEmbed
from src.decorators.command_cost import command_cost, refund
from src.entities.relationship import Relationship, RelationshipAction
from src.entities.user import User
from src.scrollables.relationship_scrollable import RelationshipScrollable
from src.ui.scrollable_embed import ScrollableEmbed
from src.utils.interaction_operations import send_scrollable

class RelationshipCommands(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="relationships", description="Display all relationships of yourself or a user")
    @app_commands.describe(member="The user you want to see the relationships of")
    @app_commands.checks.cooldown(2, 30)
    async def relationships(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if isinstance(member, discord.Member):
            if member.bot:
                return await interaction.response.send_message(embed=ErrorEmbed(title=f"ERROR", message="Bots do not have relationships."))
            user: discord.User|discord.Member = member
        else:
            user: discord.User|discord.Member = interaction.user

        scrollable = await RelationshipScrollable.create(user_ids=[str(user.id)])
        scrollable.set_user_id(str(user.id))
        embed = ScrollableEmbed(
            scrollable=scrollable,
            title="RELATIONSHIPS",
            color=discord.Color.pink(),
            author=user.display_name,
            icon_url=user.display_avatar.url
        )
        await embed.initialize()

        await send_scrollable(interaction=interaction, embed=embed)

    relationship_group = app_commands.Group(name="relationship", description="All commands about relationships")

    @relationship_group.command(name="greet", description="Greet someone c:")
    @app_commands.describe(member="The user you want to greet")
    @command_cost(amount=10, command_name="greet")
    async def greet(self, interaction: discord.Interaction, member: discord.Member):
        await run_relationship_action(
            action=RelationshipAction.GREET,
            interaction=interaction,
            member=member,
            success_verb="greets",
            fail_verb="tried to greet",
            cost=10
        )

    @relationship_group.command(name="date", description="Date someone c:")
    @app_commands.describe(member="The user you want to date")
    @command_cost(amount=50, command_name="date")
    async def date(self, interaction: discord.Interaction, member: discord.Member):
        await run_relationship_action(
            action=RelationshipAction.DATE,
            interaction=interaction,
            member=member,
            success_verb="dates",
            fail_verb="tried to date",
            cost=50
        )

    @relationship_group.command(name="hug", description="Hug someone c:")
    @app_commands.describe(member="The user you want to hug")
    @command_cost(amount=100, command_name="hug")
    async def hug(self, interaction: discord.Interaction, member: discord.Member):
        await run_relationship_action(
            action=RelationshipAction.HUG,
            interaction=interaction,
            member=member,
            success_verb="hugs",
            fail_verb="tried to hug",
            cost=100
        )

    @relationship_group.command(name="kiss", description="Kiss someone c:")
    @app_commands.describe(member="The user you want to kiss")
    @command_cost(amount=200, command_name="kiss")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member):
        await run_relationship_action(
            action=RelationshipAction.KISS,
            interaction=interaction,
            member=member,
            success_verb="kisses",
            fail_verb="tried to kiss",
            cost=200
        )

    @relationship_group.command(name="handhold", description="Hold hands with someone c:")
    @app_commands.describe(member="The user you want to hold hands with")
    @command_cost(amount=500, command_name="handhold")
    async def handhold(self, interaction: discord.Interaction, member: discord.Member):
        await run_relationship_action(
            action=RelationshipAction.HANDHOLD,
            interaction=interaction,
            member=member,
            success_verb="holds hands with",
            fail_verb="tried to hold hands with",
            cost=500
        )

    @relationship_group.command(name="status", description="Check your relationship status with someone")
    @app_commands.describe(member="The user you want to check your relationship with")
    async def status(self, interaction: discord.Interaction, member: discord.Member):
        if member.bot:
            return await interaction.response.send_message(embed=ErrorEmbed(title=f"Nope", message="Since you cant build a relationship with a bot, youre unable to display the status about it."))
        
        if interaction.user.id == member.id:
            return await interaction.response.send_message(embed=ErrorEmbed(title=f"Nope", message="Since you cant build a relationship with yourself, youre unable to display the status about it."))

        user: User = await User.load(userid=str(interaction.user.id))
        relationship: Optional[Relationship] = await user.get_relationship_with_user(str(member.id))
        
        if not isinstance(relationship, Relationship):
            return await interaction.response.send_message(embed=ErrorEmbed(title=f"No relationship", message=f"You dont have a relationship with `{member.display_name}` yet.\nTry to use `/relationship greet @user` and make sure they greet you back :3"))

        embed = discord.Embed(title=f"{interaction.user.display_name} x {member.display_name}", description=f"**`{relationship.get_rank()}`** ❥ **{relationship.points}** Points", color=discord.Color.pink())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name="Pending actions today", value=relationship.get_pending(str(interaction.user.id)), inline=False)
        next_rank, points_left = relationship.get_next_rank()
        embed.add_field(name="Next rank", value=f"**{next_rank}** `({points_left} points left)`", inline=False)
        next_action, points_left = relationship.get_next_action()
        embed.add_field(name="Next action", value=f"**{next_action}** `({points_left} points left)`", inline=False)
        await interaction.response.send_message(embed=embed)

    @relationships.error
    async def on_relationships_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        await interaction.response.send_message(embed=ErrorEmbed(title="ERROR", message=str(error)), ephemeral=True)
        
async def run_relationship_action(action: RelationshipAction, interaction: discord.Interaction, member: discord.Member, success_verb: str, fail_verb: str, cost: int) -> None:
    user: User = await User.load(userid=str(interaction.user.id))
    
    if member.bot:
        await refund(user=user, amount=cost, interaction=interaction, reason="Mentioned a bot", send_message=False)
        return await interaction.response.send_message(embed=ErrorEmbed(title=f"Seriously?", message="PLEASE just use it on a human and get a proper relationship going."))
    
    if interaction.user.id == member.id:
        await refund(user=user, amount=cost, interaction=interaction, reason="Mentioned themselves", send_message=False)
        return await interaction.response.send_message(embed=ErrorEmbed(title=f"Seriously?", message="PLEASE just use it on someone else and get a proper relationship going."))
    
    relationship = await user.load_relationship_with_user(str(member.id))

    status, message = relationship.do_action(action=action, user_id=str(interaction.user.id))
    if status:
        embed = generate_postive_embed(user=interaction.user, target=member, message=message, verb=success_verb)
    else:
        await refund(user=user, amount=cost, interaction=interaction, reason="Cant use the command yet", send_message=False)
        embed = generate_negative_embed(user=interaction.user, target=member, message=message, verb=fail_verb)
    await relationship.save()

    embed.set_footer(text="Use /relationship status @user to check your relationship")

    if status:
        await interaction.response.send_message(content=f"<@{member.id}> look!", embed=embed)
    else:
        await interaction.response.send_message(embed=embed)

def generate_postive_embed(user: discord.User|discord.Member, target: discord.Member, message: str, verb: str) -> discord.Embed:
    embed = discord.Embed(title=f"{user.display_name} {verb} {target.display_name}", timestamp=datetime.now())
    embed.color = discord.Color.pink()
    embed.description = message
    return embed

def generate_negative_embed(user: discord.User|discord.Member, target: discord.Member, message: str, verb: str) -> discord.Embed:
    embed = discord.Embed(title=f"{user.display_name} {verb} {target.display_name}", timestamp=datetime.now())
    embed.color = discord.Color.red()
    embed.description = message
    return embed

async def setup(bot: commands.Bot):
    await bot.add_cog(RelationshipCommands(bot))