import json
import socket as s

from services.cache_service import CacheService
from services.storage_service import StorageService
from utils.enums import Collection, Operation
from utils.errors import CannotCommunicateWithSocketException
from utils.socket_helper import send_to_socket, server_socket_response

class ProductRepository:
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

    def create_product(self, pid: str, data: str):
        try:
            self.__create_socket()
            product_data = json.loads(data)

            new_product = {
                "PID": pid,
                "name": product_data["name"],
                "price": str(product_data["price"]),
                "quantity": str(product_data["quantity"]),
            }

            send_to_socket(self.socket, Collection.Products, Operation.Add, pid, new_product)
            if server_socket_response(self.socket) is True:
                self.cache_service.put(Collection.Products, pid, new_product)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e
        finally:
            self.socket.close()

    def get_product_by_id(self, pid: str):
        product = self.cache_service.get(Collection.Products, pid)
        if product is not None:
            return product
        # TODO: Consultar DB
        return None

    def update_product(self, pid: str, data: dict):
        try:
            self.__create_socket()

            updated_product = {
                "PID": pid,
                "name": data["name"],
                "price": str(data["price"]),
                "quantity": str(data["quantity"]),
            }

            send_to_socket(self.socket, Collection.Products, Operation.Update, pid, updated_product)

            if server_socket_response(self.socket) is True:
                self.cache_service.put(Collection.Products, pid, updated_product)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e
        finally:
            self.socket.close()

    def delete_product(self, pid: str):
        try:
            self.__create_socket()

            send_to_socket(self.socket, Collection.Products, Operation.Delete, pid, None)

            if server_socket_response(self.socket) is True:
                self.cache_service.delete(Collection.Products, pid)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e
        finally:
            self.socket.close()

    def check_if_product_is_in_some_order(self, pid: str):
        # TODO: refatorar para usar cache e acesso ao DB
        return False
        # is_present_in_some_order = False
        # for _, order_str in hash_map["orders"].items():
        #     order = json.loads(order_str)
        #     for order_product in order["products"]:
        #         if order_product["PID"] == pid:
        #             is_present_in_some_order = True
        #             break
        #     if is_present_in_some_order:
        #         break
        # return is_present_in_some_order
