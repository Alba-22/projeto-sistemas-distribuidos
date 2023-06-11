import json
import socket as s
from typing import Tuple

from utils.enums import Operation, Collection

def send_to_socket(
        socket: s,
        collection: Collection,
        operation: Operation,
        identifier: str,
        data: dict
    ):
    socket.send(f"{collection.value}|{operation.value}|{identifier}|{json.dumps(data)}".encode())


def retrieve_from_socket(data) -> Tuple[Collection, Operation, str, str]:
    message = data.decode().split("|")
    collection = Collection[message[0]]
    operation = Operation[message[1]]
    identifier = message[2]
    data: str = message[3]
    return (collection, operation, identifier, data)

def server_socket_response(socket: s) -> bool:
    data = socket.recv(1024)
    if data.decode() == "True":
        return True
    return False
