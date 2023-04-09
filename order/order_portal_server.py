import json
import logging
import sys
from concurrent import futures

import grpc
from paho.mqtt import client as mqtt_client

from proto import api_pb2, api_pb2_grpc

hash_map = {
    "clients": {},
    "products": {},
    "orders": {},
}


class OrderPortal(api_pb2_grpc.OrderPortalServicer):
    """Provide methods that implement functionality of Order Portal Server"""

    def __init__(self, mqtt) -> None:
        self.mqtt = mqtt

    def CreateOrder(self, request, context):
        print("Creating Order", request.data)
        ...

    def RetrieveOrder(self, request, context):
        print("Retrieving Order", request.data)
        ...

    def UpdateOrder(self, request, context):
        print("Updating Order", request.data)
        ...

    def DeleteOrder(self, request, context):
        print("Deleting Order", request.data)
        ...

    def RetrieveClientOrders(self, request, context):
        print("Retrieving client orders", request.data)
        ...


def serve():
    if len(sys.argv) == 1:
        print("É necessário informar a porta que o servidor irá rodar")
        return
    port = sys.argv[1]
    if not port.isdigit():
        print("O valor passado para a porta é inválido")
        return

    mqtt = connect_mqtt
    handle_mqtt_subscribe(mqtt)

    print("Iniciando servidor gRPC na porta " + port)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc.add_OrderPortalServicer_to_server(OrderPortal(mqtt), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Servidor gRPC iniciado, ouvindo na porta " + port)
    server.wait_for_termination()


def connect_mqtt(grpc_port):
    print("Conectando ao Broker MQTT")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao Broker MQTT!")
        else:
            print("Falha ao conectar ao Broker MQTT(código %d\n", rc + ")")
            exit()

    client = mqtt_client.Client("projeto-mqtt-" + grpc_port)
    client.on_connect = on_connect
    client.connect("localhost", 1883)
    return client


def handle_mqtt_subscribe(mqtt):
    def on_subscribe_message(__, ___, msg):
        print(f"[TÓPICO = {msg.topic}] Mensagem recebida {msg.payload.decode()}")
        result = json.loads(msg.payload.decode())
        hash_map[msg.topic].append(result)
        print(hash_map)

    mqtt.subscribe("clients")
    mqtt.subscribe("products")
    mqtt.subscribe("orders")
    mqtt.on_message = on_subscribe_message


if __name__ == "__main__":
    logging.basicConfig()
    serve()
