from constants.colors import RESET, INFO, WARN, ERROR, TIMESTAMP
from utils.time import get_formatted_time

INFO_MSG = "INFO"
WARN_MSG = "WARN"
ERR_MSG = "ERROR"


class Logger:
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
    def info(msg: str, /, display_type=True, full_color=True, stamp=False, end="\n\n"):
        Logger.print(
            msg, msg_type=INFO_MSG, color=INFO, full_color=full_color, display_type=display_type, stamp=stamp, end=end
        )

    @staticmethod
    def warn(msg: str, /, display_type=True, full_color=True, stamp=False, end="\n\n"):
        Logger.print(
            msg, msg_type=WARN_MSG, color=WARN, full_color=full_color, display_type=display_type, stamp=stamp, end=end
        )

    @staticmethod
    def error(msg: str, /, display_type=True, full_color=True, stamp=False, end="\n\n"):
        Logger.print(
            msg, msg_type=ERR_MSG, color=ERROR, full_color=full_color, display_type=display_type, stamp=stamp, end=end
        )
