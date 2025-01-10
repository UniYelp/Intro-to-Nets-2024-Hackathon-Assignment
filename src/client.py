import socket
import struct

from src.utils.errors import InvalidMessageError
from src.utils.logger import Logger
from src.utils.udp import decode_udp
from src.utils.validations import validate_msg


def get_file_size():
    file_size = input("File size: ")

    if file_size.isdigit():
        return int(file_size)
    elif file_size[0:-1].isdigit():
        size = int(file_size[0:-1])
        match file_size[-1].upper():
            case "G":
                return size * 1024 * 1024 * 1024
            case "M":
                return size * 1024 * 1024
            case "K":
                return size * 1024
            case "B":
                return size
    elif file_size[0:-2].isdigit():
        unit = file_size[-2:].upper()
        size = int(file_size[0:2])

        match unit:
            case "GB":
                return size * 1024 * 1024 * 1024
            case "MB":
                return size * 1024 * 1024
            case "KB":
                return size * 1024

    Logger.warn("Invalid value. please provide a valid file size in GB/MB/KB/B")
    return get_file_size()


def get_int(msg):
    value = input(msg)
    if not value.isdigit():
        Logger.warn("Invalid Value. Must be an integer.")
        return get_int(msg)
    return value


def init():
    file_size = get_file_size()
    tcp_connections = get_int("Number of TCP connections: ")
    udp_connections = get_int("Number of UDP connections: ")
    if not tcp_connections or not udp_connections or not file_size:
        Logger.warn("Invalid inputs. please enter again.")
        return init()
    return file_size, int(tcp_connections), int(udp_connections)


def get_offer(s: socket):
    decoded_data, addr = decode_udp(s, "offer")

    validate_msg(decoded_data)

    print(f"Received message: from {addr}")
    return decoded_data, addr


def main():
    file_size, tcp_connections, udp_connections = init()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 13117))

    Logger.info("Client started, listening for offer requests...")

    while True:
        for i in range(udp_connections):
            try:
                decoded_data, addr = get_offer(s)
                print(f"Received offer from {addr} ~ {decoded_data=}")
            except struct.error | InvalidMessageError as err:
                Logger.warn(f"intercepted a message of unsupported type or size | {str(err)}", full_color=False)

        # open connections with timers
        # TODO

        print("All transfers complete, listening to offer requests")


if __name__ == "__main__":
    main()
