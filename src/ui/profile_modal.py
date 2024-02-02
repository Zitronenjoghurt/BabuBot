import discord
from discord import ui
from src.constants.custom_embeds import SuccessEmbed
from src.entities.user import User

class ProfileModal(ui.Modal):
    def __init__(self, member: discord.User | discord.Member) -> None:
        super().__init__(
            title="Customize Profile"
        )
        self.user: User = User.load(userid=str(member.id))

        self.name = ui.TextInput(label="Name", placeholder=self.user.profile.name, required=False, min_length=0, max_length=100, style=discord.TextStyle.short)
        self.add_item(self.name)

        self.pronouns = ui.TextInput(label="Pronouns", placeholder=self.user.profile.pronouns, required=False, min_length=0, max_length=100, style=discord.TextStyle.short)
        self.add_item(self.pronouns)

        self.age = ui.TextInput(label="Age", placeholder=self.user.profile.age, required=False, min_length=0, max_length=3, style=discord.TextStyle.short)
        self.add_item(self.age)

    async def on_submit(self, interaction: discord.Interaction):
        if len(self.name.value) > 0:
            self.user.profile.name = self.name.value
        if len(self.pronouns.value) > 0:
            self.user.profile.pronouns = self.pronouns.value
        if len(self.age.value) > 0:
            self.user.profile.age = self.age.value
        self.user.save()

        embed = SuccessEmbed(title="PROFILE CHANGED", message="Your profile was successfully changed c:")
        await interaction.response.send_message(embed=embed, ephemeral=True)