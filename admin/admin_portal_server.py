import logging
import random
import sys
from concurrent import futures
import traceback
from socket import socket as s

import grpc
from domain.client.client_controller import ClientController
from domain.client.client_repository import ClientRepository
from domain.product.product_repository import ProductRepository
from domain.product.product_controller import ProductController
from services.storage_service import StorageService

from proto import  api_pb2_grpc
from utils.socket_helper import operation_from_socket

class AdminPortal(api_pb2_grpc.AdminPortalServicer):
    """Provide methods that implement functionality of Admin Portal Server"""

    def __init__(self, client_controller: ClientController, product_controller: ProductController):
        self.product_controller = product_controller
        self.client_controller = client_controller

    def CreateClient(self, request, _):
        return self.client_controller.create_client(request)

    def RetrieveClient(self, request, _):
        return self.client_controller.get_client(request)

    def UpdateClient(self, request, _):
        return self.client_controller.update_client(request)

    def DeleteClient(self, request, _):
        return self.client_controller.delete_client(request)

    def CreateProduct(self, request, _):
        return self.product_controller.create_product(request)

    def RetrieveProduct(self, request, _):
        return self.product_controller.get_product(request)

    def UpdateProduct(self, request, _):
        return self.product_controller.update_product(request)

    def DeleteProduct(self, request, _):
        return self.product_controller.delete_product(request)

def serve():
    if len(sys.argv) == 1:
        print("É necessário informar a porta que o servidor irá rodar")
        return
    port = sys.argv[1]
    try:
        int(port)
    except:
        traceback.print_exc()
        print("O valor passado para a porta é inválido")
        return

    global socket

    # choosen_replic = random.randint(1, 3)
    choosen_replic = 1

    if choosen_replic == 1:
        socket_port = 20001
    elif choosen_replic == 2:
        socket_port = 20002
    else:
        socket_port = 20003

    socket = s()
    socket.connect(("localhost", socket_port))

    print(f"Socket iniciado na porta {socket_port}")

    client_repository = ClientRepository(socket)
    client_controller = ClientController(client_repository)
    product_repository = ProductRepository(socket)
    product_controller = ProductController(product_repository)

    print(f"Iniciando servidor gRPC na porta {port}...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_AdminPortalServicer_to_server(
        AdminPortal(client_controller, product_controller),
        server
    )
    server.add_insecure_port("[::]:"+ port)
    server.start()
    print("Servidor gRPC iniciado!")

    server.wait_for_termination()


if __name__ == "__main__":
    socket = None
    logging.basicConfig()
    serve()
