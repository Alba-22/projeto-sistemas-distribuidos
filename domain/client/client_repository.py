import json
import socket as s

from services.cache_service import CacheService
from services.storage_service import StorageService
from utils.enums import Collection, Operation
from utils.errors import CannotCommunicateWithSocketException
from utils.socket_helper import send_to_socket, server_socket_response


class ClientRepository:
    """
        Responsible for interating with database and cache
        to return desired information
    """

    def __init__(self, storage: StorageService):
        self.storage_service = storage
        self.cache_service = CacheService()
        self.socket = s.socket()
        self.socket_address = ("localhost", 9000)

    def __create_socket(self):
        self.socket = s.socket()
        self.socket.connect(self.socket_address)

    def create_client(self, cid: str, data: str):
        try:
            self.__create_socket()
            client_data: dict = json.loads(data)
            new_client: dict = {"CID": cid, "name": client_data["name"]}
            send_to_socket(self.socket, Collection.Clients, Operation.Add, cid, new_client)

            if server_socket_response(self.socket) is True:
                self.cache_service.put(Collection.Clients, cid, new_client)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e
        finally:
            self.socket.close()


    def get_client_by_id(self, cid: str):
        client = self.cache_service.get(Collection.Clients, cid)
        if client is not None:
            return client
        # TODO: Consultar DB
        return None

    def update_client(self, cid: str, data: str):
        try:
            self.__create_socket()
            client_data: dict = json.loads(data)
            updated_client: dict = {"CID": cid, "name": client_data["name"]}
            send_to_socket(self.socket, Collection.Clients, Operation.Update, cid, updated_client)

            if server_socket_response(self.socket) is True:
                self.cache_service.put(Collection.Clients, cid, updated_client)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e
        finally:
            self.socket.close()

    def delete_client(self, cid: str):
        try:
            self.__create_socket()
            send_to_socket(self.socket, Collection.Clients, Operation.Delete, cid, None)

            if server_socket_response(self.socket) is True:
                self.cache_service.delete(Collection.Clients, cid)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e
        finally:
            self.socket.close()
