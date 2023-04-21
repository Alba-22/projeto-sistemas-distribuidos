import json
import logging
import sys
from concurrent import futures

import grpc
from paho.mqtt import client as mqtt_client

from proto import api_pb2, api_pb2_grpc
from utils.get_by_id import get_client_by_id, get_product_by_id
from utils.on_receive_message import on_receive_message

# Operations on HashMap should follow this model:
# {
#   "key": "123",
#   "op": "ADD" | "UPDATE" | "DELETE",
#   "data": {}
# }

hash_map = {"clients": {}, "products": {}, "orders": {}}


class AdminPortal(api_pb2_grpc.AdminPortalServicer):
    """Provide methods that implement functionality of Admin Portal Server"""

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def CreateClient(self, request, _):
        try:
            client = get_client_by_id(hash_map, request.CID)
            if client is not None:
                return api_pb2.Reply(
                    error=400,
                    description=f"Já existe um cliente com o ID {request.CID}",
                )

            client_data = json.loads(request.data)
            new_client = {"CID": request.CID, "name": client_data["name"]}
            body = {
                "op": "ADD",
                "key": request.CID,
                "data": new_client,
            }
            self.mqtt.publish("clients", json.dumps(body))
            return api_pb2.Reply(error=0)
        except:
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao criar o cliente"
            )

    def RetrieveClient(self, request, _):
        try:
            client = get_client_by_id(hash_map, request.ID)
            if client is None:
                return api_pb2.Client(CID="0", data="")

            return api_pb2.Client(
                CID=client["CID"], data=json.dumps({"nome": client["name"]})
            )
        except:
            return api_pb2.Client(CID="0", data="")

    def UpdateClient(self, request, _):
        try:
            client = get_client_by_id(hash_map, request.CID)
            if client is None:
                return api_pb2.Reply(
                    error=400,
                    description=f"Não há nenhum usuário com o ID {request.CID}",
                )

            client_data = json.loads(request.data)
            client_data = {"CID": request.CID, "name": client_data["name"]}
            body = {
                "op": "UPDATE",
                "key": request.CID,
                "data": client_data,
            }
            self.mqtt.publish("clients", json.dumps(body))
            return api_pb2.Reply(error=0)
        except:
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao atualizar o cliente"
            )

    def DeleteClient(self, request, _):
        try:
            client = get_client_by_id(hash_map, request.ID)
            if client is None:
                return api_pb2.Reply(
                    error=400,
                    description=f"Não há nenhum usuário com o ID {request.ID}",
                )
            body = {
                "op": "DELETE",
                "key": request.ID,
            }
            self.mqtt.publish("clients", json.dumps(body))
            return api_pb2.Reply(error=0)

        except:
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao deletar o cliente"
            )

    def CreateProduct(self, request, _):
        try:
            product = get_product_by_id(hash_map, request.PID)
            if product is not None:
                return api_pb2.Reply(
                    error=400,
                    description=f"Já existe um produto com o ID {request.PID}",
                )

            product_data = json.loads(request.data)

            # Validate values for price and quantity
            try:
                price_float = float(product_data["price"])
                if price_float < 0:
                    return api_pb2.Reply(
                        error=400,
                        description="O valor informado para preço é inválido!",
                    )

            except ValueError:
                return api_pb2.Reply(
                    error=400, description="O valor informado para preço é inválido!"
                )

            try:
                quantity_int = int(product_data["quantity"])
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

            new_product = {
                "PID": request.PID,
                "name": product_data["name"],
                "price": float(product_data["price"]),
                "quantity": int(product_data["quantity"]),
            }
            body = {
                "op": "ADD",
                "key": request.PID,
                "data": new_product,
            }
            self.mqtt.publish("products", json.dumps(body))
            return api_pb2.Reply(error=0)
        except:
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao criar o produto"
            )

    def RetrieveProduct(self, request, _):
        try:
            product = get_product_by_id(hash_map, request.ID)
            if product is None:
                return api_pb2.Product(PID="0", data="")

            return api_pb2.Product(
                PID=product["PID"],
                data=json.dumps(
                    {
                        "nome": product["name"],
                        "preço": product["price"],
                        "quantidade": product["quantity"],
                    }
                ),
            )
        except:
            return api_pb2.Product(PID="0", data="")

    def UpdateProduct(self, request, _):
        try:
            product = get_product_by_id(hash_map, request.PID)
            if product is None:
                return api_pb2.Reply(
                    error=400,
                    description=f"Não há nenhum usuário com o ID {request.PID}",
                )

            product_data = json.loads(request.data)

            # Validate values for price and quantity
            try:
                price_float = float(product_data["price"])
                if price_float < 0:
                    return api_pb2.Reply(
                        error=400,
                        description="O valor informado para preço é inválido!",
                    )

            except ValueError:
                return api_pb2.Reply(
                    error=400, description="O valor informado para preço é inválido!"
                )

            try:
                quantity_int = int(product_data["quantity"])
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

            product_data = {
                "PID": request.PID,
                "name": product_data["name"],
                "price": float(product_data["price"]),
                "quantity": int(product_data["quantity"]),
            }
            body = {
                "op": "UPDATE",
                "key": request.PID,
                "data": product_data,
            }
            self.mqtt.publish("products", json.dumps(body))
            return api_pb2.Reply(error=0)
        except:
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao atualizar o produto"
            )

    def DeleteProduct(self, request, _):
        try:
            product = get_product_by_id(hash_map, request.ID)
            if product is None:
                return api_pb2.Reply(
                    error=400,
                    description=f"Não há nenhum produto com o ID {request.ID}",
                )
            body = {
                "op": "DELETE",
                "key": request.ID,
            }
            self.mqtt.publish("products", json.dumps(body))
            return api_pb2.Reply(error=0)

        except:
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao deletar o produto"
            )


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

    print(f"Iniciando servidor gRPC na porta {port}...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_AdminPortalServicer_to_server(AdminPortal(mqtt), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Servidor gRPC iniciado!")

    mqtt.loop_forever()

    server.wait_for_termination()


def connect_mqtt(grpc_port):
    print("Conectando ao Broker MQTT...")

    def on_connect(_, __, ___, rc):
        if rc == 0:
            print("Conectado ao Broker MQTT!")
        else:
            print(f"Falha ao conectar ao Broker MQTT(código {rc})")

    client = mqtt_client.Client("projeto-mqtt-" + grpc_port)
    client.on_connect = on_connect
    client.connect("localhost", 1884)
    return client


def handle_mqtt_subscribe(mqtt):
    def on_subscribe_message(__, ___, msg):
        on_receive_message(hash_map, msg)

    mqtt.subscribe("clients")
    mqtt.subscribe("products")
    mqtt.subscribe("orders")
    mqtt.on_message = on_subscribe_message


if __name__ == "__main__":
    logging.basicConfig()
    serve()
