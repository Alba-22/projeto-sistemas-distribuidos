import logging
import random
import sys
from concurrent import futures
from socket import socket as s

import grpc
from proto import api_pb2_grpc
from domain.order.order_controller import OrderController

from domain.client.client_repository import ClientRepository
from domain.order.order_repository import OrderRepository
from domain.product.product_repository import ProductRepository

class OrderPortal(api_pb2_grpc.OrderPortalServicer):
    """Provide methods that implement functionality of Order Portal Server"""

    def __init__(self, order_controller: OrderController) -> None:
        self.order_controller = order_controller

    def CreateOrder(self, request, _):
        return self.order_controller.create_order(request)

    def RetrieveOrder(self, request, _):
        return self.order_controller.retrieve_order(request)

    def UpdateOrder(self, request, _):
        return self.order_controller.update_order(request)

    def DeleteOrder(self, request, _):
        return self.order_controller.delete_order(request)

    def RetrieveClientOrders(self, request, _):
        return self.order_controller.retrieve_client_orders(request)


def serve():
    if len(sys.argv) == 1:
        print("É necessário informar a porta que o servidor irá rodar")
        return
    port = sys.argv[1]
    if not port.isdigit():
        print("O valor passado para a porta é inválido")
        return

    global socket1
    global socket2

    choosen_replic1 = random.randint(1, 3)
    choosen_replic2 = random.randint(4, 6)

    if choosen_replic1 == 1:
        socket_port1 = 20001
    elif choosen_replic1 == 2:
        socket_port1 = 20002
    elif choosen_replic1 == 3:
        socket_port1 = 20003
    else:
        exit(-1)

    if choosen_replic2 == 4:
        socket_port2 = 20004
    elif choosen_replic2 == 5:
        socket_port2 = 20005
    elif choosen_replic2 == 6:
        socket_port2 = 20006
    else:
        exit(-1)


    socket1 = s()
    socket1.connect(("localhost", socket_port1))

    socket2 = s()
    socket2.connect(("localhost", socket_port2))

    print(f"Socket iniciado na porta {socket_port1}")
    print(f"Socket iniciado na porta {socket_port2}")

    order_repository = OrderRepository(socket1, socket2)
    client_repository = ClientRepository(socket1, socket2)
    product_repository = ProductRepository(socket1, socket2)
    order_controller = OrderController(order_repository, client_repository, product_repository)


    print(f"Iniciando servidor gRPC na porta {port}...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_OrderPortalServicer_to_server(
        OrderPortal(order_controller),
        server
    )
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Servidor gRPC iniciado")

    server.wait_for_termination()


if __name__ == "__main__":
    socket1 = None
    socket2 = None
    logging.basicConfig()
    serve()
