import socket
import struct
import os

from src.constants.app import BUFFER_SIZE
from src.utils.errors import InvalidMessageError
from src.utils.logger import Logger
from src.utils.udp import decode_udp, encode_udp
from src.utils.validations import validate_msg

udp_port = int(os.getenv("UDP_PORT", 13118))


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
    rcv_msg_type = "offer"

    data, addr = decode_udp(s, rcv_msg_type)
    data = validate_msg(data, rcv_msg_type)

    Logger.info(f"Received message: from {addr}")
    return data, addr


def main():
    try:
        file_size, tcp_connections, udp_connections = init()

        s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_udp.bind(("", udp_port))

        Logger.info("Client started, listening for offer requests...", stamp=True, display_type=False)

        while True:
            i = 0
            while i < udp_connections:
                try:
                    data, addr = get_offer(s_udp)
                    print(f"Received offer from {addr} ~ {data=}")
                    message = encode_udp("request", file_size)
                    s_udp.sendto(message, (addr[0], data[0]))
                    i += 1
                except (struct.error, InvalidMessageError) as err:
                    Logger.warn(f"intercepted a message of unsupported type or size | {str(err)}", full_color=False)

            i = 0
            while i < tcp_connections:
                try:
                    data, addr = get_offer(s_udp)
                    print(f"Received offer from {addr} ~ {data=}")
                    message = encode_udp("request", file_size)
                    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                    s_tcp.connect((addr[0], data[1]))
                    s_tcp.sendall((str(file_size) + "\n").encode())
                    response = s_tcp.recv(BUFFER_SIZE).decode()
                    s_tcp.close()
                    i += 1
                except (struct.error, InvalidMessageError) as err:
                    Logger.warn(f"intercepted a message of unsupported type or size | {str(err)}", full_color=False)
            # open connections with timers
            # TODO

            print("All transfers complete, listening to offer requests")
    except KeyboardInterrupt:
        Logger.info("Program terminated by user")


if __name__ == "__main__":
    main()
