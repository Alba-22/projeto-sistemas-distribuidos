import json
import traceback
from proto import api_pb2
from domain.order.order_repository import OrderRepository
from domain.client.client_repository import ClientRepository
from domain.product.product_repository import ProductRepository
from utils.response_messages import not_found, bad_request, ok, internal_server_error

class OrderController:
    """
        Responsible for getting the request from the gRPC, do the necessary
        validations and call repository to persist data into database/cache
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        client_repository: ClientRepository,
        product_repository: ProductRepository,
    ) -> None:
        self.order_repository = order_repository
        self.client_repository = client_repository
        self.product_repository = product_repository

    def create_order(self, request):
        try:
            client = self.client_repository.get_client_by_id( request.CID)
            if client is None:
                return not_found(f"Cliente não encontado: {request.CID}")
            existing_order = self.order_repository.get_order_by_id(request.OID)
            if existing_order is not None:
                return bad_request(f"Já existe um pedido com o ID {request.OID}")

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
                product = self.product_repository.get_product_by_id(order_item["id"])
                if product is None:
                    return not_found(f"Produto não encontado: {order_item['id']}")

                try:
                    quantity_int = int(order_item["quantity"])
                    if quantity_int < 0:
                        return bad_request("O valor informado para quantidade é inválido!")
                except ValueError:
                    return bad_request("O valor informado para quantidade é inválido!")

                if int(product["quantity"]) < quantity_int:
                    return bad_request(
                        f"Quantidade indisponível de produto com ID {product['PID']}"
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
                self.product_repository.update_product(pid=update_data["PID"], data=update_data)

            # Cria o pedido
            self.order_repository.create_order(
                oid=request.OID,
                data={
                    "OID": request.OID,
                    "CID": request.CID,
                    "products": order_products,
                },
            )

            return ok()
        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao criar o pedido")

    def retrieve_order(self, request):
        try:
            order = self.order_repository.get_order_by_id(request.ID)
            if order is None:
                return api_pb2.Order(OID="0", CID="0", data="")

            named_products = []
            for order_product in order["products"]:
                product = self.product_repository.get_product_by_id(order_product["PID"])
                if product is None:
                    return api_pb2.Order(OID="0", CID="0", data="")
                named_products.append({**order_product, "name": product["name"]})

            return api_pb2.Order(
                OID=order["OID"],
                CID=order["CID"],
                data=json.dumps({"products": named_products}),
            )
        except:
            traceback.print_exc()
            return api_pb2.Order(OID="0", CID="0", data="")


    def update_order(self, request):
        try:
            client = self.client_repository.get_client_by_id(request.CID)
            if client is None:
                return not_found(f"Cliente não encontado: {request.CID}")
            order = self.order_repository.get_order_by_id(request.OID)
            if order is None or order["CID"] != client["CID"]:
                return not_found(f"Pedido não encontado: {request.OID}")

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
                    product = self.product_repository.get_product_by_id(order_product["id"])
                    if product is None:
                        return not_found(f"Produto não encontado: {order_product['id']}")

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
            self.order_repository.update_order(
                request.OID,
                data={
                    "OID": request.OID,
                    "CID": request.CID,
                    "products": final_order_products,
                }
            )

            # Atualiza produtos
            for update_data in product_updates_to_publish:
                self.product_repository.update_product(
                    pid=update_data["PID"],
                    data=update_data
                )

            return ok()

        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao editar o pedido")


    def delete_order(self, request):
        # VOLTAR A QUANTIDADE DOS ITENS DO PEDIDO
        # TODO: tratativa delete product
        try:
            order = self.order_repository.get_order_by_id(request.ID)
            if order is None:
                return bad_request(f"Não há nenhum pedido com o ID {request.ID}")

            # Voltar a quantidade dos produtos no banco, caso o pedido tenha produtos
            for deleting_product in order["products"]:
                original_product = self.product_repository.get_product_by_id(
                    deleting_product["PID"]
                )
                updated_product = {
                    "PID": original_product["PID"],
                    "name": original_product["name"],
                    "price": original_product["price"],
                    "quantity": str(
                        int(original_product["quantity"])
                        + int(deleting_product["quantity"])
                    ),
                }
                self.product_repository.update_product(deleting_product["PID"], updated_product)

            # Deletar pedido
            self.order_repository.delete_order(request.ID)
            return ok()

        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao deletar o pedido")


    def retrieve_client_orders(self, request):
        try:
            if self.client_repository.get_client_by_id(request.ID) is None:
                yield

            client_id = request.ID
            all_orders = self.order_repository.get_all_orders()
            for order in all_orders:
                if order["CID"] == client_id:
                    named_products = []
                    for order_product in order["products"]:
                        product = self.product_repository.get_product_by_id(order_product["PID"])
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
        product = self.product_repository.get_product_by_id(product_pid)
        if product is None:
            return not_found(f"Produto não encontado: {product_pid}")

        # typecasts
        try:
            new_o_product_quantity_int = int(new_order_quantity)
            order_product_quantity = int(current_order_quantity)
            current_product_quantity = int(product["quantity"])
        except ValueError:
            return bad_request("O valor informado para quantidade é inválido!")

        amount_to_add = order_product_quantity - new_o_product_quantity_int
        if current_product_quantity + amount_to_add < 0:
            return bad_request(f"Produto indisponível para operação: {product_pid}")

        return {
            "PID": product["PID"],
            "name": product["name"],
            "price": product["price"],
            "quantity": str(current_product_quantity + amount_to_add),
        }
