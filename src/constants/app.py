MAGIC_COOKIE = 0xABCDDCBA

UDP_MSG_TYPE = {"offer": 0x2, "request": 0x3, "payload": 0x4}

CLIENT_STATE = {"Startup", "Lookup", "SpeedTest"}

UDP_FMT = "!IBHH"  # Format string: 4 bytes for MAGIC_COOKIE, 1 byte for MESSAGE_TYPE, 2 bytes for UDP and TCP ports,
