import socket
import struct
import os

from constants.app import BUFFER_SIZE
from utils.errors import InvalidMessageError
from utils.logger import Logger
from utils.udp import decode_udp, encode_udp
from utils.validations import validate_msg

udp_port = int(os.getenv("UDP_PORT", 13118))


def get_file_size():
    """
    prompts the user for a file size until input is valid.
    supported formats: <int>GB, <int>MB, <int>KB, <int>G, <int>M, <int>K, <int>B, <int>
    :return:
        size: file size in bytes
    """
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
    """
    prompt the user for an int until input is valid
    :param msg:
        message to display while prompting
    :return:
        value: int input
    """
    value = input(msg)
    if not value.isdigit():
        Logger.warn("Invalid Value. Must be an integer.")
        return get_int(msg)
    return value


def init():
    """
    prompts the user for init variables
    :return:
        file_size: size of file to request in bytes
        tcp_connections: number of tcp connections to open
        udp_connections: number of udp connections to open
    """
    file_size = get_file_size()
    tcp_connections = get_int("Number of TCP connections: ")
    udp_connections = get_int("Number of UDP connections: ")
    if not tcp_connections or not udp_connections or not file_size:
        Logger.warn("Invalid inputs. please enter again.")
        return init()
    return file_size, int(tcp_connections), int(udp_connections)


def get_offer(s: socket) -> (tuple[int, int], tuple[str, int]):
    """
    returns the first UDP offer message it encounters
    :param s:  UDP socket
    :return:
        data: tuple[udp_port, tcp_port]
        addr: tuple[ip_addr, udp_port]
    """
    found_message = False
    while not found_message:
        rcv_msg_type = "offer"

        try:
            data, addr = decode_udp(s, rcv_msg_type)
            data = validate_msg(data, rcv_msg_type)
            Logger.info(f"Received message: from {addr}")
            return data, addr
        except (os.error, struct.error, InvalidMessageError) as err:
            Logger.warn(f"intercepted a message of unsupported type or size | {str(err)}", full_color=False)


def handle_udp(s_udp: socket, addr: str, port: int, file_size: int):
    message = encode_udp("request", file_size)
    s_udp.sendto(message, (addr, port))


def handle_tcp(addr: str, port: int, file_size: int):
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s_tcp.connect((addr, port))

    message = str(file_size) + "\n"
    s_tcp.sendall(message.encode())

    response = s_tcp.recv(BUFFER_SIZE).decode()

    s_tcp.close()


def main():
    try:
        file_size, tcp_connections, udp_connections = init()

        s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_udp.bind(("", udp_port))

        Logger.info("Client started, listening for offer requests...", stamp=True, display_type=False)

        while True:
            data, addr = get_offer(s_udp)
            server_ip_address = addr[0]
            server_tcp_port = data[1]
            server_udp_port = data[0]

            print(f"Received offer from {server_ip_address}")

            for i in range(udp_connections):
                handle_udp(s_udp, server_ip_address, server_udp_port, file_size)

            for i in range(tcp_connections):
                handle_tcp(server_ip_address, server_tcp_port, file_size)

            # open connections with timers
            # TODO

            print("All transfers complete, listening to offer requests")
    except KeyboardInterrupt:
        Logger.info("Program terminated by user")


if __name__ == "__main__":
    main()
