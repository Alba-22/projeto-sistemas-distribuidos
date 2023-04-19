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


def show_database():
    print("> CLIENTES")
    for key in hash_map["clients"]:
        print(f"{key} -> {hash_map['clients'][key]}")
    print("> PRODUTOS")
    for key in hash_map["products"]:
        print(f"{key} -> {hash_map['products'][key]}")
    print("> PEDIDOS")
    for key in hash_map["orders"]:
        print(f"{key} -> {hash_map['orders'][key]}")


class OrderPortal(api_pb2_grpc.OrderPortalServicer):
    """Provide methods that implement functionality of Order Portal Server"""

    def __init__(self, mqtt) -> None:
        self.mqtt = mqtt

    def CreateOrder(self, request, context):
        print("Creating Order", request.data)
        try:
            client = self.get_client_by_id(request.CID)
            if client is None:
                return api_pb2.Reply(
                    error=404, description=f"Cliente não encontado: {request.CID}"
                )
            existing_order = self.get_order_by_id(request.OID)
            if existing_order is not None:
                return api_pb2.Reply(
                    error=400, description=f"Já existe um pedido com o ID {request.OID}"
                )

            # request.data: json encoded list [{"id": ... , "quantity": str}]
            order_data: list[dict] = json.loads(request.data)

            product_updates_to_publish = []
            for order_item in order_data:
                # Verifica disponibilidade de produto e quantidade.
                product = self.get_product_by_id(order_item["id"])
                if product is None:
                    return api_pb2.Reply(
                        error=404,
                        description=f"Produto não encontado: {order_item['id']}",
                    )

                try:
                    quantity_int = int(order_item["quantity"])
                    if quantity_int < 0:
                        return api_pb2.Reply(
                            error=400,
                            description="O valor informado para quantidade é inválido!",
                        )
                except ValueError:
                    return api_pb2.Reply(
                        error=400,
                        description="O valor informado para quantidade é inválido!",
                    )

                if product["quantity"] < quantity_int:
                    return api_pb2.Reply(
                        error=400,
                        description=f"Quantidade indisponível de produto com ID {product['id']}",
                    )

                # Ajusta quantidade disponível de produto, se necessário.
                product_updates_to_publish.append(
                    {
                        "op": "UPDATE",
                        "key": product["id"],
                        "data": {
                            "PID": product["id"],
                            "name": product["name"],
                            "price": product["price"],
                            "quantity": product["quantity"] - quantity_int,
                        },
                    }
                )

            # Executa a operação e retorna código de erro/sucesso.
            # TODO
        except:
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao criar o pedido"
            )

    def RetrieveOrder(self, request, context):
        print("Retrieving Order", request.data)

    def UpdateOrder(self, request, context):
        print("Updating Order", request.data)

    def DeleteOrder(self, request, context):
        print("Deleting Order", request.data)

    def RetrieveClientOrders(self, request, context):
        print("Retrieving client orders", request.data)

    def get_client_by_id(self, client_id: str):
        clients = hash_map["clients"]
        for key in clients.keys():
            if key == client_id:
                return clients[key]
        return None

    def get_order_by_id(self, order_id: str):
        orders = hash_map["orders"]
        for key in orders:
            if key == order_id:
                return orders[key]
        return None

    def get_product_by_id(self, product_id: str):
        products = hash_map["products"]
        for key in products.keys():
            if key == product_id:
                return products[key]
        return None


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
