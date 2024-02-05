import discord
from discord import app_commands
import logging
import logging.handlers

class LC:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREY = '\033[90m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class FileFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: f"%(asctime)s %(levelname)s    %(name)s %(message)s",
        logging.INFO: f"%(asctime)s %(levelname)s     %(name)s %(message)s",
        logging.WARNING: f"%(asctime)s %(levelname)s  %(name)s %(message)s",
        logging.ERROR: f"%(asctime)s %(levelname)s    %(name)s %(message)s",
        logging.CRITICAL: f"%(asctime)s %(levelname)s %(name)s %(message)s"
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: f"{LC.GREY}{LC.BOLD}%(asctime)s{LC.ENDC} {LC.CYAN}{LC.BOLD}%(levelname)s{LC.ENDC}    %(name)s %(message)s",
        logging.INFO: f"{LC.GREY}{LC.BOLD}%(asctime)s{LC.ENDC} {LC.BLUE}{LC.BOLD}%(levelname)s{LC.ENDC}     %(name)s {LC.BLUE}%(message)s",
        logging.WARNING: f"{LC.GREY}{LC.BOLD}%(asctime)s{LC.ENDC} {LC.YELLOW}{LC.BOLD}%(levelname)s{LC.ENDC}  %(name)s {LC.YELLOW}%(message)s",
        logging.ERROR: f"{LC.GREY}{LC.BOLD}%(asctime)s{LC.ENDC} {LC.RED}{LC.BOLD}%(levelname)s{LC.ENDC}    %(name)s {LC.RED}%(message)s",
        logging.CRITICAL: f"{LC.GREY}{LC.BOLD}%(asctime)s{LC.ENDC} {LC.RED}{LC.BOLD}%(levelname)s %(name)s %(message)s"
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

class BotLogger:
    def __init__(self, log_file='bot.log'):
        self.logger = logging.getLogger("BOT")
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(log_file)
        stream_handler = logging.StreamHandler()

        file_handler.setLevel(logging.DEBUG)
        stream_handler.setLevel(logging.INFO)

        file_handler.setFormatter(FileFormatter())
        stream_handler.setFormatter(ColoredFormatter())

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        # Setup discord file logger
        discord_logger = logging.getLogger('discord')
        discord_logger.setLevel(logging.DEBUG)
        discord_logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

BOTLOGGER = BotLogger()
LOGGER = BOTLOGGER.get_logger()