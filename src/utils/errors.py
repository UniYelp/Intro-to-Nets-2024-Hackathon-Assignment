class InvalidMessageError(ValueError):
    def __init__(self):
        super().__init__("Received invalid message. Magic cookie or message type are invalid.")
