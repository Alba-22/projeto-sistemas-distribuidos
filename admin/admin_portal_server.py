import json
import logging

# from proto import api_pb2
# import proto.api_pb2
import sys
import uuid
from concurrent import futures

import grpc
from paho.mqtt import client as mqtt_client

from proto import api_pb2, api_pb2_grpc

# from proto import api_pb2 as api
# import proto.api_pb2_grpc as apigrpc

hash_map = {"clients": [], "products": [], "orders": []}


class AdminPortal(api_pb2_grpc.AdminPortalServicer):
    """Provide methods that implement functionality of Admin Portal Server"""

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def CreateClient(self, request, context):
        print("Creating Client " + request.data)
        client_data = json.loads(request.data)
        new_client = {"CID": request.CID, "name": client_data.name}
        self.mqtt.publish("clients", json.dumps(new_client))
        return api_pb2.Reply(error=0)


def serve():
    if len(sys.argv) == 1:
        print("É necessário informar a porta que o servidor irá rodar")
        return
    port = sys.argv[1]
    try:
        int(port)
    except:
        print("O valor passado para a porta é inválido")
        return

    mqtt = connect_mqtt(port)
    handle_mqtt_subscribe(mqtt)

    print("Iniciando servidor gRPC na porta " + port)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_AdminPortalServicer_to_server(AdminPortal(mqtt), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Servidor gRPC iniciado")

    mqtt.loop_forever()

    server.wait_for_termination()


def connect_mqtt(grpc_port):
    print("Conectando ao Broker MQTT")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao Broker MQTT!")
        else:
            print("Falha ao conectar ao Broker MQTT(código %d\n", rc + ")")
            exit

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
