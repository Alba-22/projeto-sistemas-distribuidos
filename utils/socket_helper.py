import json
from socket import socket as s
from typing import Optional, Tuple

from utils.enums import Operation, Collection

def operation_to_socket(
        socket: s,
        collection: Collection,
        operation: Operation,
        identifier: str,
        data: dict
    ):
    if data is not None:
        socket.send(f"{collection.value}|{operation.value}|{identifier}|{json.dumps(data)}".encode())
    else:
        socket.send(f"{collection.value}|{operation.value}|{identifier}|None".encode())


def operation_from_socket(socket: s) -> Tuple[Collection, Operation, str, str]:
    data = socket.recv(1024)
    message = data.decode().split("|")
    collection = Collection[message[0]]
    operation = Operation[message[1]]
    identifier = message[2]
    data: str = message[3]
    return (collection, operation, identifier, data)

def message_to_socket(socket: s, message: Optional[dict]):
    print(f"msg_to_socket: {message}")
    if message is None:
        socket.send("None".encode())
    else:
        socket.send(json.dumps(message).encode())

def message_from_socket(socket: s) -> Optional[dict]:
    data = socket.recv(1024)
    decoded = data.decode()
    print(f"msg_from_socket: {decoded}")
    if decoded == "None":
        return None
    return json.loads(decoded)