import socket
import struct
import os
import threading
import time

from constants.app import BUFFER_SIZE
from utils.inputs import get_file_size_input, get_int
from utils.errors import InvalidMessageError
from utils.logger import Logger, LogLevels
from utils.udp import decode_udp, encode_udp, decode_header_udp
from utils.validations import validate_msg

udp_port = int(os.getenv("UDP_PORT", 13118))
Logger._log_level = LogLevels.ERROR


def init():
    """
    prompts the user for init variables
    :return:
        file_size: size of file to request in bytes
        tcp_connections: number of tcp connections to open
        udp_connections: number of udp connections to open
    """
    file_size = get_file_size_input()
    tcp_connections = get_int("Number of TCP connections: ")
    udp_connections = get_int("Number of UDP connections: ")

    return file_size, int(tcp_connections), int(udp_connections)


def get_offer(s: socket) -> tuple[tuple[int, int], tuple[str, int]]:
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


def handle_udp(s_udp: socket, addr: str, port: int, file_size: int, id: int):
    msg_type = "request"
    message = encode_udp(msg_type, file_size)
    s_udp.sendto(message, (addr, port))

    msg_type = "payload"
    count = 0
    start_time = time.time()
    s_udp.settimeout(1)

    while count < file_size:
        try:
            (decoded_data, payload), addr = decode_header_udp(s_udp, msg_type)
            validate_msg(decoded_data, msg_type)
            count += len(payload)
            Logger.debug(f"[UDP THREAD {id}] received next udp chunk, got {count/file_size*100:.2f}% of file")
        except struct.error:
            continue
        except socket.timeout:
            break

    end_time = time.time()
    elapsed_time = end_time - start_time

    Logger.info(f"""
    UDP transfer #{id} finished,
    total time: {elapsed_time:.6f} seconds, total speed: {count/elapsed_time} bits/second,
    percentage of packets received successfully: {count/file_size*100:.2f}%
    """, display_type=False, stamp=True)


def handle_tcp(addr: str, port: int, file_size: int, id: int):
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s_tcp.connect((addr, port))

    message = str(file_size) + "\n"
    s_tcp.sendall(message.encode())

    count = 0
    start_time = time.time()
    # get all the chunks
    while count < file_size:
        msg = s_tcp.recv(BUFFER_SIZE)
        count += len(msg)
        Logger.debug(f"[TCP THREAD {id}]: received next tcp chunk, got {count / file_size * 100:.2f}% of file")

    s_tcp.close()
    end_time = time.time()
    elapsed_time = end_time - start_time

    Logger.info(f"""
    TCP transfer #{id} finished,
    total time: {elapsed_time:.6f} seconds, total speed: {count/elapsed_time} bits/second,
    percentage of packets received successfully: {count/file_size*100:.2f}%
    """, display_type=False, stamp=True)


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
                udp_thread = threading.Thread(target=handle_udp, args=(s_udp, server_ip_address, server_udp_port, file_size, i + 1))
                udp_thread.daemon = True
                udp_thread.start()
                # handle_udp(s_udp, server_ip_address, server_udp_port, file_size)

            for i in range(tcp_connections):
                tcp_thread = threading.Thread(target=handle_tcp,
                                              args=(server_ip_address, server_tcp_port, file_size, i + 1))
                tcp_thread.daemon = True
                tcp_thread.start()
                # handle_tcp(server_ip_address, server_tcp_port, file_size)

            for thread in threading.enumerate():
                if thread is not threading.main_thread():
                    thread.join()

            print("All transfers complete, listening to offer requests")
    except KeyboardInterrupt:
        Logger.info("Program terminated by user")


if __name__ == "__main__":
    main()
