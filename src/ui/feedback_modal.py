import discord
from discord import ui
from src.constants.custom_embeds import SuccessEmbed
from src.entities.feedback import Feedback
from src.entities.user import User

class FeedbackModal(ui.Modal):
    def __init__(self, member: discord.User | discord.Member) -> None:
        super().__init__(
            title="Feedback or Ideas"
        )
        self.user: User = User.load(userid=str(member.id))

        self.text = ui.TextInput(label="Feedback", placeholder="This command has a 5 minute cooldown, so put everything you want into this one field (if you can).", required=True, min_length=25, max_length=1000, style=discord.TextStyle.paragraph)
        self.add_item(self.text)

    async def on_submit(self, interaction: discord.Interaction):
        feedback = Feedback(
            creator_id=self.user.userid, 
            text=self.text.value
        )
        feedback.save()
        embed = SuccessEmbed(title="FEEDBACK SUBMITTED", message="Your feedback was successfully submitted and I will review it as soon as I can!")
        await interaction.response.send_message(embed=embed, ephemeral=True)