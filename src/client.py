import socket
import struct

from src.constants.app import UDP_FMT
from src.utils.errors import InvalidMessageError
from src.utils.logger import Logger
from src.utils.validations import is_msg_valid, validate_msg


def init():
    # Todo: input validation
    file_size = input("File size: ")
    tcp_connections = input("Number of TCP connections: ")
    udp_connections = input("Number of UDP connections: ")
    return file_size, int(tcp_connections), int(udp_connections)


def get_offer(s: socket):
    data, addr = s.recvfrom(1024)  # Buffer size is 1024 bytes
    decoded_data = struct.unpack(UDP_FMT, data)

    validate_msg(decoded_data)

    print(f"Received message: from {addr}")
    return decoded_data, addr


def main():
    file_size, tcp_connections, udp_connections = init()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 13117))

    Logger.info("Client started, listening for offer requests...")

    while True:
        for i in range(udp_connections):
            try:
                decoded_data, addr = get_offer(s)
                print(f"Received offer from {addr}")
            except InvalidMessageError as err:
                Logger.warn(str(err))

        # open connections with timers
        # TODO

        print("All transfers complete, listening to offer requests")


if __name__ == '__main__':
    main()
