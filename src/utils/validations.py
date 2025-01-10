from src.constants.app import MAGIC_COOKIE, UDP_MSG_TYPE
from src.utils.errors import InvalidMessageError, UnexpectedMessageError


def is_msg_valid(msg: tuple):
    return msg[0] == MAGIC_COOKIE and msg[1] in UDP_MSG_TYPE.values()


def validate_msg(msg: tuple):
    if not is_msg_valid(msg):
        raise InvalidMessageError()


def validate_msg_type(msg: tuple, msg_type: str):
    if not msg[1] == msg_type:
        raise UnexpectedMessageError()
