import json
import logging
import sys
from concurrent import futures
import traceback

import grpc
from paho.mqtt import client as mqtt_client

from proto import api_pb2, api_pb2_grpc
from utils.get_by_id import get_client_by_id, get_order_by_id, get_product_by_id
from utils.on_receive_message import on_receive_message

hash_map = {"clients": {}, "products": {}, "orders": {}}


class OrderPortal(api_pb2_grpc.OrderPortalServicer):
    """Provide methods that implement functionality of Order Portal Server"""

    def __init__(self, mqtt) -> None:
        self.mqtt = mqtt

    def CreateOrder(self, request, context):
        try:
            client = get_client_by_id(hash_map, request.CID)
            if client is None:
                return api_pb2.Reply(
                    error=404, description=f"Cliente não encontado: {request.CID}"
                )
            existing_order = get_order_by_id(hash_map, request.OID)
            if existing_order is not None:
                return api_pb2.Reply(
                    error=400, description=f"Já existe um pedido com o ID {request.OID}"
                )

            # request.data: json encoded list [{"id": ... , "quantity": str}, ...]
            order_data: list[dict] = json.loads(request.data)

            # Trata dois itens na lista com mesmo PID
            order_data_dict = {}
            for order_item in order_data:
                if order_data_dict.get(order_item["id"], None) is None:
                    order_data_dict[order_item["id"]] = order_item
                else:
                    order_data_dict[order_item["id"]]["quantity"] = str(
                        int(order_data_dict[order_item["id"]]["quantity"])
                        + int(order_item["quantity"])
                    )

            product_updates_to_publish = []
            order_products = []
            for _, order_item in order_data_dict.items():
                # Verifica disponibilidade de produto e quantidade.
                product = get_product_by_id(hash_map, order_item["id"])
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

                if int(product["quantity"]) < quantity_int:
                    return api_pb2.Reply(
                        error=400,
                        description=f"Quantidade indisponível de produto com ID {product['PID']}",
                    )

                # Ajusta quantidade disponível de produto, se necessário.
                product_updates_to_publish.append(
                    {
                        "PID": product["PID"],
                        "name": product["name"],
                        "price": product["price"],
                        "quantity": str(int(product["quantity"]) - quantity_int),
                    }
                )
                order_products.append(
                    {
                        "PID": product["PID"],
                        "price": product["price"],
                        "quantity": str(quantity_int),
                    }
                )

            for update_data in product_updates_to_publish:
                self.mqtt.publish(
                    "products",
                    json.dumps(
                        {
                            "op": "UPDATE",
                            "key": update_data["PID"],
                            "data": update_data,
                        }
                    ),
                )

            # Cria o pedido
            self.mqtt.publish(
                "orders",
                json.dumps(
                    {
                        "op": "ADD",
                        "key": request.OID,
                        "data": {
                            "OID": request.OID,
                            "CID": request.CID,
                            "products": order_products,
                        },
                    }
                ),
            )

            return api_pb2.Reply(error=0)
        except:
            traceback.print_exc()
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao criar o pedido"
            )

    def RetrieveOrder(self, request, context):
        try:
            order = get_order_by_id(hash_map, request.ID)
            if order is None:
                raise ValueError()

            named_products = []
            for order_product in order["products"]:
                product = get_product_by_id(hash_map, order_product["PID"])
                if product is None:
                    raise ValueError()
                named_products.append({**order_product, "name": product["name"]})

            return api_pb2.Order(
                OID=order["OID"],
                CID=order["CID"],
                data=json.dumps({"products": named_products}),
            )
        except:
            traceback.print_exc()
            return api_pb2.Order(OID="0", CID="0", data="")

    def UpdateOrder(self, request, context):
        try:
            client = get_client_by_id(hash_map, request.CID)
            if client is None:
                return api_pb2.Reply(
                    error=404, description=f"Cliente não encontado: {request.CID}"
                )
            order = get_order_by_id(hash_map, request.OID)
            if order is None or order["CID"] != client["CID"]:
                return api_pb2.Reply(
                    error=404, description=f"Pedido não encontado: {request.OID}"
                )

            # request.data: json encoded list [{"id": str , "quantity": str}, ...]
            request_data: list[dict] = json.loads(request.data)
            # Trata dois itens na lista com mesmo PID
            order_updates_dict = {}
            for product_order in request_data:
                if order_updates_dict.get(product_order["id"], None) is None:
                    order_updates_dict[product_order["id"]] = product_order
                else:
                    order_updates_dict[product_order["id"]]["quantity"] = str(
                        int(order_updates_dict[product_order["id"]]["quantity"])
                        + int(product_order["quantity"])
                    )

            final_order_products = []
            product_updates_to_publish = []

            # Trata atualizações de produtos que já estão naquele pedido
            # (atualizações de quantidade e remoção)
            for order_product in order["products"]:
                new_order_product = order_updates_dict.get(order_product["PID"], None)

                if new_order_product is None:
                    # produto no pedido original não será alterado
                    final_order_products.append(order_product)
                    continue

                # Contabiliza que aquela atualização já será processada
                # (Sobrarão nesse dicionário as atualizações de adição de novos itens,
                # que serão tratadas posteriormente)
                del order_updates_dict[order_product["PID"]]

                # TODO: impedir modificações quando o preço entre a tabela de orders e products

                # se a quantidade for "0", aquele produto é retirado da lista
                # (mas o resto das tratativas acontece do mesmo jeito)
                if new_order_product["quantity"] != "0":
                    final_order_products.append(
                        {
                            "PID": order_product["PID"],
                            "price": order_product["price"],
                            "quantity": new_order_product["quantity"],
                        }
                    )

                # Trata atualizações quantidade produtos
                propagation = self.propagate_product_updates(
                    product_pid=order_product["PID"],
                    current_order_quantity=order_product["quantity"],
                    new_order_quantity=new_order_product["quantity"],
                )
                if isinstance(propagation, api_pb2.Reply):
                    return propagation
                product_updates_to_publish.append(propagation)

            # Trata inserção de novos produtos no pedido
            for _, order_product in order_updates_dict.items():
                if order_product["quantity"] != "0":
                    product = get_product_by_id(hash_map, order_product["id"])
                    if product is None:
                        return api_pb2.Reply(
                            error=404,
                            description=f"Produto não encontado: {order_product['id']}",
                        )

                    final_order_products.append(
                        {
                            "PID": product["PID"],
                            "price": product["price"],
                            "quantity": order_product["quantity"],
                        }
                    )

                    # Trata atualizações quantidade produtos
                    propagation = self.propagate_product_updates(
                        product_pid=order_product["id"],
                        current_order_quantity="0",
                        new_order_quantity=order_product["quantity"],
                    )
                    if isinstance(propagation, api_pb2.Reply):
                        return propagation
                    product_updates_to_publish.append(propagation)

            # Atualiza ordem
            self.mqtt.publish(
                "orders",
                json.dumps(
                    {
                        "op": "UPDATE",
                        "key": request.OID,
                        "data": {
                            "OID": request.OID,
                            "CID": request.CID,
                            "products": final_order_products,
                        },
                    }
                ),
            )

            # Atualiza produtos
            for update_data in product_updates_to_publish:
                self.mqtt.publish(
                    "products",
                    json.dumps(
                        {
                            "op": "UPDATE",
                            "key": update_data["PID"],
                            "data": update_data,
                        }
                    ),
                )

            return api_pb2.Reply(error=0)

        except:
            traceback.print_exc()
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao editar o pedido"
            )

    def propagate_product_updates(
        self,
        product_pid: str,
        current_order_quantity: str,
        new_order_quantity: str,
    ) -> dict:
        """
        Propaga alterações nas quantidades de produtos de acordo com as
        alterações dos pedidos.

        Retorna entrada atualizada na tabela de Products
        """
        product = get_product_by_id(hash_map, product_pid)
        if product is None:
            return api_pb2.Reply(
                error=404,
                description=f"Produto não encontado: {product_pid}",
            )

        # typecasts
        try:
            new_o_product_quantity_int = int(new_order_quantity)
            order_product_quantity = int(current_order_quantity)
            current_product_quantity = int(product["quantity"])
        except ValueError:
            return api_pb2.Reply(
                error=400,
                description="O valor informado para quantidade é inválido!",
            )

        amount_to_add = order_product_quantity - new_o_product_quantity_int
        if current_product_quantity + amount_to_add < 0:
            return api_pb2.Reply(
                error=400,
                description=f"Produto indisponível para operação: {product_pid}",
            )

        return {
            "PID": product["PID"],
            "name": product["name"],
            "price": product["price"],
            "quantity": str(current_product_quantity + amount_to_add),
        }

    def DeleteOrder(self, request, context):
        # VOLTAR A QUANTIDADE DOS ITENS DO PEDIDO
        # TODO: tratativa delete product
        try:
            order = get_order_by_id(hash_map, request.ID)
            if order is None:
                return api_pb2.Reply(
                    error=400,
                    description=f"Não há nenhum pedido com o ID {request.ID}",
                )

            # Voltar a quantidade dos produtos no hash_map, caso o pedido tenha produtos
            for deleting_product in order["products"]:
                original_product = get_product_by_id(hash_map, deleting_product["PID"])
                updated_product = {
                    "PID": original_product["PID"],
                    "name": original_product["name"],
                    "price": original_product["price"],
                    "quantity": str(
                        int(original_product["quantity"])
                        + int(deleting_product["quantity"])
                    ),
                }
                self.mqtt.publish(
                    "products",
                    json.dumps(
                        {
                            "op": "UPDATE",
                            "key": deleting_product["PID"],
                            "data": updated_product,
                        }
                    ),
                )

            # Deletar pedido
            self.mqtt.publish(
                "orders",
                json.dumps(
                    {
                        "op": "DELETE",
                        "key": request.ID,
                    }
                ),
            )
            return api_pb2.Reply(error=0)

        except:
            traceback.print_exc()
            return api_pb2.Reply(
                error=500, description="Ocorreu um erro ao deletar o pedido"
            )

    def RetrieveClientOrders(self, request, context):
        try:
            if get_client_by_id(hash_map, request.ID) is None:
                yield

            client_id = request.ID
            for _, order_str in hash_map["orders"].items():
                order = json.loads(order_str)
                if order["CID"] == client_id:
                    named_products = []
                    for order_product in order["products"]:
                        product = get_product_by_id(hash_map, order_product["PID"])
                        if product is None:
                            raise ValueError()
                        named_products.append(
                            {**order_product, "name": product["name"]}
                        )

                    yield api_pb2.Order(
                        OID=order["OID"],
                        CID=order["CID"],
                        data=json.dumps({"products": named_products}),
                    )
        except:
            traceback.print_exc()
            yield


def serve():
    if len(sys.argv) == 1:
        print("É necessário informar a porta que o servidor irá rodar")
        return
    port = sys.argv[1]
    if not port.isdigit():
        print("O valor passado para a porta é inválido")
        return

    mqtt = connect_mqtt(port)
    handle_mqtt_subscribe(mqtt)

    print(f"Iniciando servidor gRPC na porta {port}...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    api_pb2_grpc.add_OrderPortalServicer_to_server(OrderPortal(mqtt), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Servidor gRPC iniciado")

    mqtt.loop_forever()

    server.wait_for_termination()


def connect_mqtt(grpc_port):
    print("Conectando ao Broker MQTT...")

    def on_connect(_, __, ___, rc):
        if rc == 0:
            print("Conectado ao Broker MQTT!")
        else:
            print("Falha ao conectar ao Broker MQTT(código %d\n", rc + ")")
            exit()

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
