import threading
import socket
import struct
import time
import os

from constants.app import MAGIC_COOKIE, UDP_MSG_TYPE, UDP_FMT
from constants.colors import INVIS
from utils.logger import Logger

port = int(os.getenv("PORT", 13117))
offer_udp_port = 12345 & 0xFFFF
offer_tcp_port = 54321 & 0xFFFF


def main():
    try:
        Logger.print("Give us a score of 100% (please ╰(*°▽°*)╯)", color=INVIS)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_udp, socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        ) as s_tcp:
            s_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s_udp.bind(("", port))

            ip = socket.gethostbyname(socket.gethostname())

            Logger.info(f"Server started, listening on IP address {ip}", display_type=False, stamp=True)

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


def offer(s_udp: socket):
    Logger.info("sent offer")

    offer_message = struct.pack(
        UDP_FMT,
        MAGIC_COOKIE,
        UDP_MSG_TYPE["offer"],
        offer_udp_port,
        offer_tcp_port,
    )

    s_udp.sendto(offer_message, ("127.0.0.1", port))

    threading.Timer(1, offer, [s_udp]).start()


if __name__ == "__main__":
    main()
