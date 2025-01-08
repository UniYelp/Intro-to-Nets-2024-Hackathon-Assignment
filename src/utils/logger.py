from constants.colors import ERROR, INFO, RESET, TIMESTAMP
from utils.time import get_formatted_time

INFO_MSG = 'INFO'
ERR_MSG = 'ERROR'


class Logger():
    @staticmethod
    def print(msg: str, /, color: str, full_color=True, end="\n\n", type: str = None):
        print(f"{color}{f"{type}:{RESET if not full_color else ""} " if type is not None else ""}{
              msg}{RESET}", end=end)

    @staticmethod
    def stamp():
        Logger.print(f"{get_formatted_time()}>", color=TIMESTAMP, end=' ')

    @staticmethod
    def info(msg: str, /, full_color: bool = True, end: str = "\n\n", stamp=False):
        if stamp:
            Logger.stamp()
        Logger.print(msg, type=INFO_MSG, color=INFO,
                     full_color=full_color, end=end)

    @staticmethod
    def error(msg: str, /, full_color: bool = True, end: str = "\n\n", stamp=False):
        if stamp:
            Logger.stamp()
        Logger.print(msg, type=ERR_MSG, color=ERROR,
                     full_color=full_color, end=end)
