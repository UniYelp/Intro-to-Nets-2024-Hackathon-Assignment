from constants.app import MAGIC_COOKIE, UDP_MSG_TYPE
from utils.errors import InvalidMessageError, UnexpectedMessageError


def is_msg_valid(msg: tuple):
    return msg[0] == MAGIC_COOKIE and msg[1] in UDP_MSG_TYPE.values()


def validate_msg(msg: tuple, msg_type: str):
    if not is_msg_valid(msg):
        raise InvalidMessageError()
    validate_msg_type(msg, msg_type)
    return msg[2:]


def validate_msg_type(msg: tuple, msg_type: str):
    if not msg[1] == UDP_MSG_TYPE[msg_type]:
        raise UnexpectedMessageError()
