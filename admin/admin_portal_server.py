import json
import logging
import sys
from concurrent import futures

import grpc
from paho.mqtt import client as mqtt_client

from proto import api_pb2, api_pb2_grpc

# Operations on HashMap should follow this model:
# {
#   "key": "123",
#   "op": "ADD" | "UPDATE" | "DELETE",
#   "data": {}
# }

hash_map = {"clients": {}, "products": {}, "orders": {}}

def show_database():
    print("> CLIENTES")
    for key in hash_map["clients"].keys():
        print(f"{key} -> {hash_map['clients'][key]}")
    print("> PRODUTOS")
    for key in hash_map["products"].keys():
        print(f"{key} -> {hash_map['products'][key]}")
    print("> PEDIDOS")
    for key in hash_map["orders"].keys():
        print(f"{key} -> {hash_map['orders'][key]}")
  

class AdminPortal(api_pb2_grpc.AdminPortalServicer):
    """Provide methods that implement functionality of Admin Portal Server"""

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def CreateClient(self, request, _):
        try:
            client = self.get_client_by_id(request.CID)
            if client is not None:
                return api_pb2.Reply(error=400, description=f"Já existe um cliente com o ID {request.CID}")

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
            return api_pb2.Reply(error=500, description=f"Ocorreu um erro ao criar o cliente")
    
    def RetrieveClient(self, request, _):
        try:
            client = self.get_client_by_id(request.ID)
            if client is None:
                return api_pb2.Client(CID="", data="")
                # return api_pb2.Reply(error=404, description=f"Não há nenhum usuário com o ID {request.ID}")

            return api_pb2.Client(CID=client["CID"], data=json.dumps({"nome": client["name"]}))
        except:
            return api_pb2.Client(CID="", data="")
            # return api_pb2.Reply(error=500, description=f"Ocorreu um erro ao obter os dados do cliente")

    def get_client_by_id(self, client_id: str):
        clients = hash_map["clients"]
        for key in clients.keys():
            if key == client_id:
                return clients[key]
        return None
    
    def UpdateClient(self, request, _):
        try:
            client = self.get_client_by_id(request.CID)
            if client is None:
                return api_pb2.Reply(error=400, description=f"Não há nenhum usuário com o ID {request.CID}")

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
            return api_pb2.Reply(error=500, description=f"Ocorreu um erro ao atualizar o cliente")
    
    def DeleteClient(self, request, _):
        try:
            client = self.get_client_by_id(request.ID)
            if client is None:
                return api_pb2.Reply(error=400, description=f"Não há nenhum usuário com o ID {request.ID}")
            body = {
                "op": "DELETE",
                "key": request.ID,
            }
            self.mqtt.publish("clients", json.dumps(body))
            return api_pb2.Reply(error=0)

        except:
            return api_pb2.Reply(error=500, description=f"Ocorreu um erro ao deletar o cliente")
    
    def CreateProduct(self, request, _):
        try:
            product = self.get_product_by_id(request.PID)
            if product is not None:
                return api_pb2.Reply(error=400, description=f"Já existe um produto com o ID {request.PID}")

            product_data = json.loads(request.data)

            # Validate values for price and quantity
            try:
                price_float = float(product_data["price"])
                if (price_float < 0):
                    return api_pb2.Reply(error=400, description=f"O valor informado para preço é inválido!")
                              
            except ValueError:
                    return api_pb2.Reply(error=400, description=f"O valor informado para preço é inválido!")
            
            try:
                quantity_int = int(product_data["quantity"])
                if (quantity_int < 0):
                    return api_pb2.Reply(error=400, description=f"O valor informado para quantidade é inválido!")
                              
            except ValueError:
                    return api_pb2.Reply(error=400, description=f"O valor informado para quantidade é inválido!")

            new_product = {"PID": request.PID, "name": product_data["name"], "price": product_data["price"], "quantity": product_data["quantity"]}
            body = {
                "op": "ADD",
                "key": request.PID,
                "data": new_product,
            }
            self.mqtt.publish("products", json.dumps(body))
            return api_pb2.Reply(error=0)
        except:
            return api_pb2.Reply(error=500, description=f"Ocorreu um erro ao criar o produto")

    def RetrieveProduct(self, request, _):
        try:
            product = self.get_product_by_id(request.ID)
            if product is None:
                return api_pb2.Product(PID="", data="")
                # return api_pb2.Reply(error=404, description=f"Não há nenhum usuário com o ID {request.ID}")

            return api_pb2.Product(PID=product["PID"], data=json.dumps({"nome": product["name"], "preço": product["price"], "quantidade": product["quantity"]}))
        except:
            return api_pb2.Product(PID="", data="")
            # return api_pb2.Reply(error=500, description=f"Ocorreu um erro ao obter os dados do cliente")

    def get_product_by_id(self, product_id: str):
        products = hash_map["products"]
        for key in products.keys():
            if key == product_id:
                return products[key]
        return None
    
    def DeleteProduct(self, request, _):
        try:
            product = self.get_product_by_id(request.ID)
            if product is None:
                return api_pb2.Reply(error=400, description=f"Não há nenhum produto com o ID {request.ID}")
            body = {
                "op": "DELETE",
                "key": request.ID,
            }
            self.mqtt.publish("products", json.dumps(body))
            return api_pb2.Reply(error=0)

        except:
            return api_pb2.Reply(error=500, description=f"Ocorreu um erro ao deletar o produto")

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
        print(f"[TÓPICO = {msg.topic}] Mensagem recebida: {msg.payload.decode()}")
        result = json.loads(msg.payload.decode())
        if result["op"] == "ADD":
            hash_map[msg.topic][result["key"]] = result["data"]
        elif result["op"] == "UPDATE":
            hash_map[msg.topic][result["key"]] = result["data"]
        elif result["op"] == "DELETE":
            del hash_map[msg.topic][result["key"]]
 
        show_database()

    mqtt.subscribe("clients")
    mqtt.subscribe("products")
    mqtt.subscribe("orders")
    mqtt.on_message = on_subscribe_message


if __name__ == "__main__":
    logging.basicConfig()
    serve()
