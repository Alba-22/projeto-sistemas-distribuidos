class CannotCommunicateWithSocketException(Exception):
    def __init__(self, message: str):
        if message is None:
            self.message = "Não foi possível comunicar com a base de dados"
        else:
            self.message = message
