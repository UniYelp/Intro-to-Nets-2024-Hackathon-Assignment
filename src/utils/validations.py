from src.constants.app import MAGIC_COOKIE, UDP_MSG_TYPE
from .errors import InvalidMessageError, UnexpectedMessageError


def is_msg_valid(msg: tuple):
    """
    Validating that the received message starts with the MAGIC_COOKIE and is of one of the supported types
    """
    return msg[0] == MAGIC_COOKIE and msg[1] in UDP_MSG_TYPE.values()


def validate_msg_type(msg: tuple, msg_type: str):
    """
    Validating that the received message is of the expected message type.
    Throws if not of expected type
    """
    if not msg[1] == UDP_MSG_TYPE[msg_type]:
        raise UnexpectedMessageError()


def validate_msg(msg: tuple, msg_type: str):
    """
    Validating that the received message is a valid message, and that it is of the expected message type.
    Throws if not valid or not of expected type
    """
    if not is_msg_valid(msg):
        raise InvalidMessageError()
    validate_msg_type(msg, msg_type)
    # returns a tuple of the data after stripping the MAGIC_COOKIE and the message type off of it
    return msg[2:]
