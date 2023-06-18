import json
import traceback
from domain.order.order_repository import OrderRepository
from domain.product.product_repository import ProductRepository
from proto import api_pb2
from utils.response_messages import bad_request, internal_server_error, not_found, ok


class ProductController:
    """
        Responsible for getting the request from the gRPC, do the necessary
        validations and call repository to persist data into database/cache
    """

    def __init__(self, product_repository: ProductRepository, order_repository: OrderRepository) -> None:
        self.product_repository = product_repository
        self.order_repository = order_repository

    def create_product(self, request):
        try:
            product = self.product_repository.get_product_by_id(request.PID)
            if product is not None:
                return bad_request(f"Já existe um produto com o ID {request.PID}")

            # Validate values for price and quantity
            product_data = json.loads(request.data)
            try:
                price_float = float(product_data["price"])
                if price_float < 0:
                    return bad_request("O valor informado para preço é inválido!")

            except ValueError:
                return bad_request("O valor informado para preço é inválido!")

            try:
                quantity_int = int(product_data["quantity"])
                if quantity_int < 0:
                    return bad_request("O valor informado para quantidade é inválido!")

            except ValueError:
                return bad_request("O valor informado para quantidade é inválido!")

            self.product_repository.create_product(request.PID, request.data)
            return ok()
        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao criar o produto")

    def get_product(self, request):
        try:
            product = self.product_repository.get_product_by_id(request.ID, check_cache=True)
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
            traceback.print_exc()
            return api_pb2.Product(PID="0", data="")

    def update_product(self, request):
        try:
            product = self.product_repository.get_product_by_id(request.PID)
            if product is None:
                return not_found(f"Não há nenhum usuário com o ID {request.PID}")

            if self.order_repository.check_if_product_is_in_some_order(product["PID"]):
                return bad_request(
                    "Não é possível atualizar o produto, pois ele já está presente em um pedido"
                )

            product_data = json.loads(request.data)

            # Validate values for price and quantity
            try:
                price_float = float(product_data["price"])
                if price_float < 0:
                    return bad_request("O valor informado para preço é inválido!")

            except ValueError:
                return bad_request("O valor informado para preço é inválido!")

            try:
                quantity_int = int(product_data["quantity"])
                if quantity_int < 0:
                    return bad_request("O valor informado para quantidade é inválido!")

            except ValueError:
                return bad_request("O valor informado para quantidade é inválido!")

            self.product_repository.update_product(request.PID, product_data)
            return ok()
        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao atualizar o produto")

    def delete_product(self, request):
        try:
            product = self.product_repository.get_product_by_id(request.ID)
            if product is None:
                return not_found(f"Não há nenhum produto com o ID {request.ID}")

            if self.order_repository.check_if_product_is_in_some_order(request.ID):
                return bad_request(
                    "Não é possível remover o produto, pois ele já está presente em um pedido"
                )

            self.product_repository.delete_product(request.ID)
            return ok()
        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao deletar o produto")
