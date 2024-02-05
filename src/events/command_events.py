import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from src.logging.logger import LOGGER
import time

class CommmandEvents(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.command_start_times = {}

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.type == discord.InteractionType.application_command:
            return
        
        command_name, command_args = get_command_name_and_args(interaction)
        self.command_start_times[interaction.id] = time.time()
        LOGGER.debug(f"Command {command_name} started by {interaction.user.name} ({interaction.user.id}) with arguments {str(command_args)}")
        self.bot.loop.create_task(self.check_command_completion(interaction.id, command_name, interaction.user.id))

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command | app_commands.ContextMenu):
        command_name = get_full_command_path(command)
        start_time = self.command_start_times.pop(interaction.id, None)
        if start_time is not None:
            execution_time = time.time() - start_time
            LOGGER.debug(f"Command {command_name} by {interaction.user.name} ({interaction.user.id}) was successfully executed in {execution_time:.2f} seconds")
        else:
            LOGGER.debug(f"Command {command_name} by {interaction.user.name} ({interaction.user.id}) was successfully executed but start time was not recorded")

    async def check_command_completion(self, interaction_id: int, command_name: str, user_id: int):
        await asyncio.sleep(120)
        if interaction_id in self.command_start_times:
            LOGGER.error(f"Command {command_name} started by user ID {user_id} did not complete after 120 seconds.")
            self.command_start_times.pop(interaction_id, None)

async def setup(bot):
    await bot.add_cog(CommmandEvents(bot))

def get_command_name_and_args(interaction: discord.Interaction) -> tuple[str, dict]:
    if not isinstance(interaction, discord.Interaction) or not interaction.data:
        return 'unknown', {}
    
    command_name = interaction.data['name'] if 'name' in interaction.data else 'unknown'
    command_args = {}

    options = interaction.data.get('options', [])

    for option in options:
        if option.get('type') not in (1, 2):
            continue

        command_name += f" {option['name']}"
        args = option.get("options", [])
        for arg in args:
            command_args[arg.get("name", "no name")] = arg.get("value", "no value")
    
    return command_name, command_args

def get_full_command_path(command: app_commands.Command | app_commands.ContextMenu):
    return command.qualified_name