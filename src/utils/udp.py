import socket
import struct

from src.constants.app import MAGIC_COOKIE, UDP_MSG_FMT, UDP_MSG_TYPE, BUFFER_SIZE


def encode_udp(msg_type: str, *data):
    """
    Packing the message's data together with the MAGIC_COOKIE & MSG_TYPE based on the type's expected format
    """
    return struct.pack(UDP_MSG_FMT[msg_type], MAGIC_COOKIE, UDP_MSG_TYPE[msg_type], *data)


def decode_udp(s_udp: socket, msg_type: str):
    """
    Unpacking the received message's data based on the type's expected format
    """
    data, addr = s_udp.recvfrom(BUFFER_SIZE)
    decoded_data = struct.unpack(UDP_MSG_FMT[msg_type], data)
    return decoded_data, addr
