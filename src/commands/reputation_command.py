import discord
from discord import app_commands
from discord.ext import commands
from src.constants.custom_embeds import ErrorEmbed
from src.entities.user import User

class ReputationCommand(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @app_commands.command(name="rep", description="Give the specified user a reputation point")
    @app_commands.describe(member="The user you want to give a reputation point")
    async def reputation(self, interaction: discord.Interaction, member: discord.Member):
        if member.bot:
            embed = ErrorEmbed("You cant rep a bot!", "Please only rep actual users! c:")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user: User = User.load(userid=str(interaction.user.id))
        if not user.reputation.can_do_rep():
            embed = ErrorEmbed("You already gave reputation today!", f"You can give your next reputation point {user.reputation.next_rep_discord_stamp()}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        target: User = User.load(userid=str(member.id))
        user.rep_user(target)
        user.save()
        target.save()

        embed = discord.Embed(
            title="REPUTATION RECEIVED", 
            description=f"**`{member.display_name}`** received a reputation point from **`{interaction.user.display_name}`**",
            color=discord.Color.from_str("#a6f558")
        )
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        embed.add_field(name="CURRENT POINTS", value=f"**`{member.display_name}`** now has **{target.reputation.points_received}** points!")
        if user.reputation.points_given == 1:
            embed.set_footer(text="You can only send one reputation point per day!")

        await interaction.response.send_message(f"<@{member.id}>", embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReputationCommand(bot))