from src.utils.file_operations import construct_path, files_in_directory

COMMAND_EXTENSIONS_PATH = "src/commands/"
EVENTS_EXTENSIONS_PATH = "src/events/"

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