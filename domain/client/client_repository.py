import json
from typing import Optional
from socket import socket as s

from services.cache_service import CacheService
from utils.decide_chord import decide_chord
from utils.enums import Collection, Operation
from utils.errors import CannotCommunicateWithSocketException
from utils.socket_helper import operation_to_socket, message_from_socket


class ClientRepository:
    """
        Responsible for interating with database and cache
        to return desired information
    """

    def __init__(self, socket1: s, socket2: s):
        self.cache_service = CacheService()
        self.socket1 = socket1
        self.socket2 = socket2


    def create_client(self, cid: str, data: str):
        try:
            client_data: dict = json.loads(data)
            new_client: dict = {"CID": cid, "name": client_data["name"]}
            choosen_socket = decide_chord(cid, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Clients, Operation.Add, cid, new_client)

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.put(Collection.Clients, cid, new_client)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e

    def get_client_by_id(self, cid: str, check_cache: bool = False) -> Optional[dict]:
        if check_cache is True:
            client = self.cache_service.get(Collection.Clients, cid)
            if client is not None:
                return client
        try:
            choosen_socket = decide_chord(cid, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Clients, Operation.Get, cid, None)
            result = message_from_socket(choosen_socket)
            if result is not None:
                self.cache_service.put(Collection.Clients, cid, result)
            return result
        except CannotCommunicateWithSocketException as e:
            raise e

    def update_client(self, cid: str, data: str):
        try:
            client_data: dict = json.loads(data)
            updated_client: dict = {"CID": cid, "name": client_data["name"]}

            choosen_socket = decide_chord(cid, self.socket1, self.socket2)
            operation_to_socket(
                choosen_socket,
                Collection.Clients,
                Operation.Update,
                cid,
                updated_client
            )

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.put(Collection.Clients, cid, updated_client)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e

    def delete_client(self, cid: str):
        try:
            choosen_socket = decide_chord(cid, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Clients, Operation.Delete, cid, None)

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.delete(Collection.Clients, cid)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e
