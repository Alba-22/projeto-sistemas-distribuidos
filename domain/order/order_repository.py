from socket import socket as s
from services.cache_service import CacheService
from utils.enums import Collection, Operation
from utils.socket_helper import operation_to_socket, message_from_socket
from utils.errors import CannotCommunicateWithSocketException
from utils.decide_chord import decide_chord

class OrderRepository:
    """
        Responsible for interating with database and cache
        to return desired information
    """

    def __init__(self, socket1: s, socket2: s) -> None:
        self.cache_service = CacheService()
        self.socket1 = socket1
        self.socket2 = socket2

    def create_order(self, oid: str, data: dict):
        try:
            choosen_socket = decide_chord(oid, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Orders, Operation.Add, oid, data)

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.put(Collection.Orders, oid, data)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e

    def get_order_by_id(self, order_id: str, check_cache: bool = False):
        if check_cache:
            order = self.cache_service.get(Collection.Orders, order_id)
            if order is not None:
                return order
        try:
            choosen_socket = decide_chord(order_id, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Orders, Operation.Get, order_id, None)
            result = message_from_socket(choosen_socket)
            if result is not None:
                self.cache_service.put(Collection.Orders, order_id, result)
            return result
        except CannotCommunicateWithSocketException as e:
            raise e

    def update_order(self, order_id: str, data: dict):
        try:
            choosen_socket = decide_chord(order_id, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Orders, Operation.Update, order_id, data)

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.delete(Collection.Orders, order_id)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e

    def delete_order(self, order_id: str):
        try:
            choosen_socket = decide_chord(order_id, self.socket1, self.socket2)
            operation_to_socket(choosen_socket, Collection.Orders, Operation.Delete, order_id, None)

            if message_from_socket(choosen_socket) is not None:
                self.cache_service.delete(Collection.Orders, order_id)
            else:
                raise CannotCommunicateWithSocketException(None)
        except CannotCommunicateWithSocketException as e:
            raise e

    def get_all_orders(self) -> list[dict]:
        try:
            orders = []
            for socket in (self.socket1, self.socket2):
                operation_to_socket(
                    socket, Collection.Orders, Operation.List, None, None
                )
                result = message_from_socket(socket)
                
                orders.extend(result)

            # Preenche cache
            for order in orders:
                self.cache_service.put(Collection.Orders, order["OID"], order)

            return orders
        except CannotCommunicateWithSocketException as e:
            raise e


    def check_if_product_is_in_some_order(self, pid: str):
        is_present_in_some_order = False
        for order in self.get_all_orders():
            for order_product in order["products"]:
                if order_product["PID"] == pid:
                    is_present_in_some_order = True
                    break
            if is_present_in_some_order:
                break
        return is_present_in_some_order
