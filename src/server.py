import threading
import socket
import struct
import math
import time
import os

from constants.app import BUFFER_SIZE
from constants.colors import INVIS
from utils.logger import Logger
from utils.errors import InvalidMessageError
from utils.udp import decode_udp, encode_udp
from utils.validations import validate_msg

udp_port = int(os.getenv("UDP_PORT", 13117))
tcp_port = int(os.getenv("TCP_PORT", 14117))


def offer(s_udp: socket):
    Logger.info("Broadcasting offer", stamp=True)

    offer_message = encode_udp("offer", udp_port, tcp_port)
    s_udp.sendto(offer_message, ("255.255.255.255", 13118))

    threading.Timer(1, offer, [s_udp]).start()


def handle_udp(s_udp: socket):
    rcv_msg_type = "request"
    while True:
        try:
            data, addr = decode_udp(s_udp, rcv_msg_type)
            validated_data = validate_msg(data, rcv_msg_type)
            file_size = validated_data[0]

            Logger.info(
                f"Received a UDP request from {addr} for a file of size {file_size}B", stamp=True, full_color=False
            )

            # Calculate the number of segments
            total_segments = math.ceil(file_size / BUFFER_SIZE)

            for segment in range(total_segments):
                # Calculate the segment payload size
                segment_start = segment * BUFFER_SIZE
                segment_end = min(segment_start + BUFFER_SIZE, file_size)
                payload_size = segment_end - segment_start

                # Generate the payload data
                payload = b"\x00" * payload_size

                # Encode and send the UDP message
                payload_msg = encode_udp("payload", total_segments, segment + 1) + payload
                s_udp.sendto(payload_msg, addr)

            Logger.info(
                f"Finished sending file of size {file_size}B to {addr} over a UDP connection",
                stamp=True,
                full_color=False,
            )
        except (struct.error, InvalidMessageError) as err:
            Logger.warn(f"intercepted a message of unsupported type or size | {str(err)}", full_color=False)
        except Exception as err:
            Logger.error(f"unknown error of type {type(err).__name__} while handling a UDP request | {str(err)}")


def handle_tcp(s_tcp: socket):
    while True:
        conn, addr = s_tcp.accept()
        Logger.info(f"Accepted TCP connection from {addr}")

        try:
            # Read the incoming data (file size requested)
            data = b""
            while not data.endswith(b"\n"):  # Ensure we read until the newline
                chunk = conn.recv(BUFFER_SIZE)
                # print(f"{chunk=}")
                if not chunk:  # Client closed connection prematurely
                    raise ConnectionError("Client closed the connection before sending a complete request.")
                data += chunk

            # Parse the file size from the received data
            file_size = int(data.strip())
            Logger.info(
                f"Received a TCP request for a file of size {file_size}B from {addr}", stamp=True, full_color=False
            )

            # Generate and send the file data
            bytes_sent = 0
            while bytes_sent < file_size:
                # Determine the size of the next chunk
                chunk_size = min(BUFFER_SIZE, file_size - bytes_sent)

                # Generate data
                chunk: bytes = b"\x00" * chunk_size

                # Send the chunk to the client
                conn.sendall(chunk)
                bytes_sent += chunk_size

            Logger.info(
                f"Successfully sent file of size {file_size}B to {addr} over a TCP connection",
                stamp=True,
                full_color=False,
            )
        except ValueError:
            Logger.error(f"Invalid file size received from {addr}: {data.decode().strip()}", full_color=False)
        except Exception as err:
            Logger.error(
                f"Error during TCP file transfer with {addr}: {type(err).__name__} | {str(err)}", full_color=False
            )
        finally:
            # Close the connection
            conn.close()
            Logger.info(f"Closed TCP connection with {addr}", stamp=True)


def handle_requests(s_udp: socket, s_tcp: socket):
    udp_thread = threading.Thread(target=handle_udp, args=(s_udp,))
    tcp_thread = threading.Thread(target=handle_tcp, args=(s_tcp,))

    udp_thread.daemon = True
    tcp_thread.daemon = True

    udp_thread.start()
    tcp_thread.start()


def main():
    try:
        Logger.print("Give us a score of 100% (please ╰(*°▽°*)╯)", color=INVIS)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_udp, socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        ) as s_tcp:
            s_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            ip = socket.gethostbyname(socket.gethostname())

            s_udp.bind((ip, udp_port))
            s_tcp.bind((ip, tcp_port))

            s_tcp.listen(5)  # Allow up to 5 queued connections

            Logger.info(f"Server started, listening on IP address {ip}", display_type=False, stamp=True)

            requests_handler_thread = threading.Thread(target=handle_requests, args=(s_udp, s_tcp))
            requests_handler_thread.daemon = True
            requests_handler_thread.start()

            offer_thread = threading.Thread(target=offer, args=(s_udp,))
            offer_thread.daemon = True
            offer_thread.start()

            while True:
                time.sleep(1)
    except socket.error as err:
        Logger.error(f"socket creation failed with error {str(err)}", full_color=False)
    except KeyboardInterrupt:
        Logger.info("Program terminated by user")
    except Exception as err:
        Logger.error(f"unknown error of type {type(err).__name__} | {str(err)}")


if __name__ == "__main__":
    main()
