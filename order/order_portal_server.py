from concurrent import futures
import logging

import grpc
import proto.api_pb2
import proto.api_pb2_grpc as grpc

def serve():
    port = '50051'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc.add_OrderPortalServicer_to_server(OrderPortal(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()

class OrderPortal(grpc.CreateOrder):
    print("Creating Order")