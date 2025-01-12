from enum import Enum

from src.constants.colors import RESET, INFO, WARN, ERROR, TIMESTAMP, DEBUG
from .stamp import get_formatted_time


class LogLevels(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


class Logger:
    _log_level: LogLevels = LogLevels.INFO

    @classmethod
    @property
    def log_level(cls):
        return cls._log_level

    @staticmethod
    def print(
            msg: str, /, color: str, msg_type: str = None, display_type=True, full_color=True, stamp=False, end="\n\n"
    ):
        if stamp:
            Logger.stamp()
        mid = f"{msg_type}:{RESET if not full_color else ''} " if msg_type is not None and display_type else ""
        print(f"{color}{mid}{msg}{RESET}", end=end)

    @staticmethod
    def stamp():
        Logger.print(f"{get_formatted_time()}>", color=TIMESTAMP, end=" ")

    @staticmethod
    def debug(msg: str, /, display_type=True, full_color=True, stamp=False, end="\n\n"):
        if Logger._log_level.value <= LogLevels.DEBUG.value:
            Logger.print(
                msg, msg_type=LogLevels.DEBUG.name, color=DEBUG, full_color=full_color, display_type=display_type,
                stamp=stamp, end=end
            )

    @staticmethod
    def info(msg: str, /, display_type=True, full_color=True, stamp=False, always_display=False, end="\n\n"):
        if always_display or Logger._log_level.value <= LogLevels.INFO.value:
            Logger.print(
                msg, msg_type=LogLevels.INFO.name, color=INFO, full_color=full_color, display_type=display_type, stamp=stamp, end=end
            )

    @staticmethod
    def warn(msg: str, /, display_type=True, full_color=True, stamp=False, end="\n\n"):
        if Logger._log_level.value <= LogLevels.WARN.value:
            Logger.print(
                msg, msg_type=LogLevels.WARN.name, color=WARN, full_color=full_color, display_type=display_type, stamp=stamp, end=end
            )

    @staticmethod
    def error(msg: str, /, display_type=True, full_color=True, stamp=False, end="\n\n"):
        if Logger._log_level.value <= LogLevels.ERROR.value:
            Logger.print(
                msg, msg_type=LogLevels.ERROR.name, color=ERROR, full_color=full_color, display_type=display_type, stamp=stamp, end=end
            )
