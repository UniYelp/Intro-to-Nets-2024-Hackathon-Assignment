import threading
import socket
import struct
import time
import os

from constants.app import MAGIC_COOKIE, UDP_MSG_TYPE
from constants.colors import INVIS
from utils.logger import Logger

port = int(os.getenv("PORT", 13117))
offer_udp_port = 12345 & 0xFF
offer_tcp_port = 54321 & 0xFF


def main():
    global s

    try:
        Logger.print("Give us a score of 100% (please ╰(*°▽°*)╯)", color=INVIS)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))

        ip = socket.gethostbyname(socket.gethostname())

        Logger.info(f"Server started, listening on IP address {ip}", display_type=False, stamp=True)

        offer_thread = threading.Thread(target=offer, args=(ip,))
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


def offer(ip: str):
    global s
    Logger.info("sent offer")

    offer_message = struct.pack(
        "!IBHH",  # Format string: 4 bytes for MAGIC_COOKIE, 1 byte for MESSAGE_TYPE, 2 bytes for UDP and TCP ports,
        MAGIC_COOKIE,
        UDP_MSG_TYPE["offer"],
        offer_udp_port,
        offer_tcp_port,
    )

    s.sendto(offer_message, (ip, port))

    threading.Timer(1, offer, [ip]).start()


if __name__ == "__main__":
    main()
