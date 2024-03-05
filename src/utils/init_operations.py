import os
import importlib.util
import inspect
from discord.ext import commands
from typing import Callable
from src.logging.logger import LOGGER
from src.utils.file_operations import construct_path, files_in_directory

COMMAND_EXTENSIONS_PATH = "src/commands/"
EVENTS_EXTENSIONS_PATH = "src/events/"
ROUTINES_PATH = "src/routines/"

def get_extensions() -> list[str]:
    command_path = construct_path(COMMAND_EXTENSIONS_PATH)
    commands_extension = COMMAND_EXTENSIONS_PATH.replace("/", ".")
    events_path = construct_path(EVENTS_EXTENSIONS_PATH)
    events_extension = EVENTS_EXTENSIONS_PATH.replace("/", ".")

    extensions = []
    for file in files_in_directory(command_path, ".py"):
        name = file[:-3]
        extensions.append(commands_extension + name)
    for file in files_in_directory(events_path, ".py"):
        name = file[:-3]
        extensions.append(events_extension + name)
    return extensions

def get_routines(bot: commands.Bot) -> list[tuple[int, Callable]]:
    routines = []
    for file_name in files_in_directory(ROUTINES_PATH, ".py"):
        file_path = os.path.join(ROUTINES_PATH, file_name)
        module_name = file_name[:-3]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            raise RuntimeError(f"An error occured while retrieving bot routines: module name {module_name} does not exist at file path {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module=module)

        if not hasattr(module, 'ACTIVE'):
            raise RuntimeError(f"Routine {module_name} has no specified ACTIVE value.")
        active = getattr(module, 'ACTIVE')
        if not active:
            LOGGER.info(f"Routine {module_name} is not active and will be skipped.")
            continue

        if not hasattr(module, 'run'):
            raise RuntimeError(f"Routine {module_name} has no run method.")
        if not inspect.iscoroutinefunction(module.run):
            raise RuntimeError(f"Run method of routine {module_name} is not asynchronous.")
        if not hasattr(module, 'INTERVAL_SECONDS'):
            raise RuntimeError(f"Routine {module_name} has no specified INTERVAL_SECONDS.")
        
        interval = getattr(module, 'INTERVAL_SECONDS')
        if interval < 1:
            raise RuntimeError(f"The intervall of routine {module_name} is too low. Has to be at least 1.")

        routines.append((interval, create_run_method(bot=bot, module=module, module_name=module_name)))
    return routines

def create_run_method(bot: commands.Bot, module, module_name: str) -> Callable:
    async def run():
        LOGGER.debug(f"Executing routine {module_name}.")
        try:
            await module.run(bot)
        except Exception as e:
            LOGGER.error(f"An error occured while executing routine {module_name}: {e}")
        LOGGER.debug(f"Finished executing routine {module_name}.")
    return run