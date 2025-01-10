class InvalidMessageError(ValueError):
    def __init__(self, msg="Received invalid message. Magic cookie or message type are invalid."):
        super().__init__(msg)


class UnexpectedMessageError(InvalidMessageError):
    def __init__(self):
        super().__init__("Received a message of an unexpected type.")
