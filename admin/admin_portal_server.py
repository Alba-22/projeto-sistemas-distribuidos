import logging
import sys
from concurrent import futures
import traceback
import socket as s

import grpc
from domain.client.client_controller import ClientController
from domain.client.client_repository import ClientRepository
from domain.product.product_repository import ProductRepository
from domain.product.product_controller import ProductController
from services.storage_service import StorageService

from proto import  api_pb2_grpc
from utils.socket_helper import retrieve_from_socket

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

    storage = StorageService("main:12000", ["partner: 130000"])
    client_repository = ClientRepository(storage)
    client_controller = ClientController(client_repository)
    product_repository = ProductRepository(storage)
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

    socket = s.socket()
    socket.bind(("localhost", 9000))
    socket.listen(3)

    while True:
        connection, address = socket.accept()
        with connection:
            print("Connected to ", address)
            collection, operation, identifier, data = retrieve_from_socket(connection.recv(1024))
            result = storage.receive_message(collection, operation, identifier, data)
            if result:
                print("Request Successful")
                connection.send("True".encode())
            else:
                print("Request Unsuccessful")
                connection.send("False".encode())
            connection.close()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
