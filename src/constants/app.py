MAGIC_COOKIE = 0xABCDDCBA

UDP_MSG = {"offer": "offer", "request": "request", "payload": "payload"}

UDP_MSG_TYPE = {"offer": 0x2, "request": 0x3, "payload": 0x4}  # dict[msg_type, type_code]

UDP_MSG_SIZE = {"offer": 9, "request": 13}  # dict[msg_type, amount_of_bytes]

BUFFER_SIZE = 1024

UDP_MSG_FMT = {
    "offer": "!IBHH",  # Format string: 4 bytes for MAGIC_COOKIE, 1 byte for MESSAGE_TYPE, 2 bytes for UDP and TCP ports
    "request": "!IBQ",  # Format string: 4 bytes for MAGIC_COOKIE, 1 byte for MESSAGE_TYPE, 8 bytes for file size
}

CLIENT_STATE: set[str] = {"Startup", "Lookup", "SpeedTest"}
