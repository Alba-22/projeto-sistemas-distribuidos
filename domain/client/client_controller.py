import json
import traceback
from domain.client.client_repository import ClientRepository
from utils.response_messages import bad_request, internal_server_error, not_found, ok
from proto import api_pb2


class ClientController:
    """
        Responsible for getting the request from the gRPC, do the necessary
        validations and call repository to persist data into database/cache
    """

    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def create_client(self, request):
        try:
            client = self.repository.get_client_by_id(request.CID)
            if client is not None:
                return bad_request(f"Já existe um cliente com o ID {request.CID}")
            self.repository.create_client(request.CID, request.data)
            return ok()
        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao criar o cliente")

    def get_client(self, request):
        try:
            client = self.repository.get_client_by_id(request.ID, check_cache=True)
            if client is None:
                return api_pb2.Client(CID="0", data="")

            return api_pb2.Client(
                CID=client["CID"], data=json.dumps({"nome": client["name"]})
            )
        except:
            traceback.print_exc()
            return api_pb2.Client(CID="0", data="")

    def update_client(self, request):
        try:
            client = self.repository.get_client_by_id(request.CID)
            if client is None:
                return not_found(f"Não há nenhum usuário com o ID {request.CID}")

            self.repository.update_client(request.CID, request.data)
            return ok()
        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao atualizar o cliente")

    def delete_client(self, request):
        try:
            client = self.repository.get_client_by_id(request.ID)
            if client is None:
                return not_found(f"Não há nenhum usuário com o ID {request.ID}")
            self.repository.delete_client(request.ID)
            return ok()
        except:
            traceback.print_exc()
            return internal_server_error("Ocorreu um erro ao deletar o cliente")
