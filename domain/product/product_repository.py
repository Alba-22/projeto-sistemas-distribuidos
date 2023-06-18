import json
from socket import socket as s

from services.cache_service import CacheService
from utils.decide_chord import decide_chord
from utils.enums import Collection, Operation
from utils.errors import CannotCommunicateWithSocketException
from utils.socket_helper import operation_to_socket, message_from_socket

class ProductRepository:
    """
        Responsible for interating with database and cache
        to return desired information
    """

    def __init__(self, socket1: s, socket2: s):
        self.cache_service = CacheService()
        self.socket1 = socket1
        self.socket2 = socket2

    def create_product(self, pid: str, data: str):
        try:
            product_data = json.loads(data)

            new_product = {
                "PID": pid,
                "name": product_data["name"],
                "price": str(product_data["price"]),
                "quantity": str(product_data["quantity"]),
            }

            choosen_socket = decide_chord(pid, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Products, Operation.Add, pid, new_product)

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.put(Collection.Products, pid, new_product)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e

    def get_product_by_id(self, pid: str, check_cache: bool = False):
        if check_cache:
            product = self.cache_service.get(Collection.Products, pid)
            if product is not None:
                return product
        try:
            choosen_socket = decide_chord(pid, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Products, Operation.Get, pid, None)
            result = message_from_socket(choosen_socket)
            if result is not None:
                self.cache_service.put(Collection.Products, pid, result)
            return result
        except CannotCommunicateWithSocketException as e:
            raise e

    def update_product(self, pid: str, data: dict):
        try:
            updated_product = {
                "PID": pid,
                "name": data["name"],
                "price": str(data["price"]),
                "quantity": str(data["quantity"]),
            }

            choosen_socket = decide_chord(pid, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Products, Operation.Update, pid, updated_product)

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.put(Collection.Products, pid, updated_product)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e

    def delete_product(self, pid: str):
        try:
            choosen_socket = decide_chord(pid, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Products, Operation.Delete, pid, None)

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.delete(Collection.Products, pid)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e
