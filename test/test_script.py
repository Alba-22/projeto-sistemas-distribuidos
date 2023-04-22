import json
import grpc

from proto import api_pb2, api_pb2_grpc


def render_retrieve_order(order_stub, oid: str):
    result = order_stub.RetrieveOrder(api_pb2.ID(ID=oid))
    data = json.loads(result.data)
    for product in data["products"]:
        for key, value in product.items():
            print(f"[-] {key}: {value}")
        print("----------------------------")


def render_update_result(result):
    if result.error == 0:
        print("Pedido alterado com sucesso!")
    else:
        print(f">>>>>>>> Erro: {result.description}")


def run():
    admin_port = 55006
    order_port = 55005
    print("A porta a ser utilizada para o OrderPortalServer é 55005!")
    print("A porta a ser utilizada para o AdminPortalServer é 55006!")
    input("Pressione qualquer tecla para continuar")
    channel = grpc.insecure_channel(f"localhost:{admin_port}")
    admin_stub = api_pb2_grpc.AdminPortalStub(channel)
    print("===========================================================================")
    print("Caso de teste: CRUD do Cliente")
    cid = "44"
    input("Pressione qualquer tecla para começar")
    print("---------------------------------------------------------------------------")
    print(f"Criando cliente com CID={cid} e name=Lewis Hamilton")
    result = admin_stub.CreateClient(
        api_pb2.Client(CID=cid, data=json.dumps({"name": "Lewis Hamilton"}))
    )
    if result.error == 0:
        print("Cliente adicionado com sucesso!")
    else:
        print(f"Erro: {result.description}")
        return

    print("---------------------------------------------------------------------------")
    print(f"Buscando cliente com CID={cid}")
    result = admin_stub.RetrieveClient(api_pb2.ID(ID="44"))
    if result.CID != "0":
        print(f"[-] ID: {result.CID}")
        data = json.loads(result.data)
        for key, value in data.items():
            print(f"[-] {key}: {value}")

    else:
        print(f"Erro: Não há nenhum cliente com o ID {cid}")
        return

    print("---------------------------------------------------------------------------")
    print(f"Atualizando dados do cliente com CID={cid}")
    result = admin_stub.UpdateClient(
        api_pb2.Client(CID=cid, data=json.dumps({"name": "Lewis Carl Hamilton"}))
    )
    if result.error == 0:
        print("Cliente atualizado com sucesso!")
    else:
        print(f"Erro: {result.description}")
        return

    print("---------------------------------------------------------------------------")
    print(f"Deletando cliente com CID={cid}")
    result = admin_stub.DeleteClient(api_pb2.ID(ID=cid))
    if result.error == 0:
        print("Cliente deletado com sucesso!")
    else:
        print(f"Erro: {result.description}")
        return
    print("===========================================================================")
    print("Caso de teste: CRUD do Produto")
    input("Pressione qualquer tecla para começar")
    pid = "13"
    print("---------------------------------------------------------------------------")
    print("Criando produto com PID=13")
    result = admin_stub.CreateProduct(
        api_pb2.Product(
            PID=pid,
            data=json.dumps(
                {
                    "name": "Carro W13",
                    "price": 1250,
                    "quantity": 5,
                }
            ),
        )
    )
    if result.error == 0:
        print("Produto adicionado com sucesso!")
    else:
        print(f"Erro: {result.description}")
        return

    print("---------------------------------------------------------------------------")
    print("Obtendo produto com PID=13")
    result = admin_stub.RetrieveProduct(api_pb2.ID(ID=pid))
    if len(result.PID) != 0:
        print(f"[-] ID: {result.PID}")
        data = json.loads(result.data)
        for key, value in data.items():
            print(f"[-] {key}: {value}")

    else:
        print(f"Erro: Não há nenhum produto com o ID {pid}")
        return

    print("---------------------------------------------------------------------------")
    print("Atualizando produto com PID=13")
    result = admin_stub.UpdateProduct(
        api_pb2.Product(
            PID=pid,
            data=json.dumps(
                {
                    "name": "Carro Mercedes W13",
                    "price": 3450,
                    "quantity": 10,
                },
            ),
        ),
    )
    if result.error == 0:
        print("Produto atualizado com sucesso!")
    else:
        print(f"Erro: {result.description}")
        return

    print("---------------------------------------------------------------------------")
    print("Deletando produto com PID=13")
    result = admin_stub.DeleteProduct(api_pb2.ID(ID=pid))
    if result.error == 0:
        print("Produto deletado com sucesso!")
    else:
        print(f"Erro: {result.description}")

    print("===========================================================================")
    print("Caso de teste: Operações com o Pedido")
    input("Pressione qualquer tecla para começar")
    cid = "2"
    pid1 = "1"
    pid2 = "2"
    oid = "10"
    channel = grpc.insecure_channel(f"localhost:{order_port}")
    order_stub = api_pb2_grpc.OrderPortalStub(channel)
    # Criar cliente
    admin_stub.CreateClient(
        api_pb2.Client(CID=cid, data=json.dumps({"name": "Dustin"}))
    )
    # Criar produtos
    admin_stub.CreateProduct(
        api_pb2.Product(
            PID=pid1,
            data=json.dumps(
                {
                    "name": "Caneta",
                    "price": "2.5",
                    "quantity": "8",
                }
            ),
        )
    )
    admin_stub.CreateProduct(
        api_pb2.Product(
            PID=pid2,
            data=json.dumps(
                {
                    "name": "Lapis",
                    "price": "3",
                    "quantity": "9",
                }
            ),
        )
    )
    # Criar pedido
    print("Criando pedido com um produto")
    result = order_stub.CreateOrder(
        api_pb2.Order(
            OID=oid, CID=cid, data=json.dumps([{"id": pid1, "quantity": "3"}])
        )
    )
    if result.error == 0:
        print("Pedido criado com sucesso!")
    else:
        print(f"Erro: {result.description}")
        return
    print("---------------------------------------------------------------------------")
    input("Pressione qualquer tecla para continuar")
    print("Atualizando pedido diminuindo a quantidade")
    order_stub.UpdateOrder(
        api_pb2.Order(
            OID=oid, CID=cid, data=json.dumps([{"id": pid1, "quantity": "2"}])
        )
    )
    render_retrieve_order(order_stub, oid)
    print("---------------------------------------------------------------------------")
    input("Pressione qualquer tecla para continuar")
    print("Atualizando pedido aumentando a quantidade")
    order_stub.UpdateOrder(
        api_pb2.Order(
            OID=oid, CID=cid, data=json.dumps([{"id": pid1, "quantity": "4"}])
        )
    )
    render_retrieve_order(order_stub, oid)
    print("---------------------------------------------------------------------------")
    input("Pressione qualquer tecla para continuar")
    print("Atualizando adicionando PID 2")
    result = order_stub.UpdateOrder(
        api_pb2.Order(
            OID=oid,
            CID=cid,
            data=json.dumps([{"id": pid2, "quantity": "5"}]),
        )
    )
    render_update_result(result)
    render_retrieve_order(order_stub, oid)

    print("---------------------------------------------------------------------------")
    input("Pressione qualquer tecla para continuar")
    print("Atualizando removendo PID 1")
    result = order_stub.UpdateOrder(
        api_pb2.Order(
            OID=oid,
            CID=cid,
            data=json.dumps([{"id": pid1, "quantity": "0"}]),
        )
    )
    render_update_result(result)
    render_retrieve_order(order_stub, oid)

    print("---------------------------------------------------------------------------")
    input("Pressione qualquer tecla para continuar")
    print("Atualizando 2 vezes o PID 2")
    result = order_stub.UpdateOrder(
        api_pb2.Order(
            OID=oid,
            CID=cid,
            data=json.dumps(
                [
                    {"id": pid2, "quantity": "2"},
                    {"id": pid2, "quantity": "4"},
                ],
            ),
        )
    )

    render_update_result(result)
    render_retrieve_order(order_stub, oid)


if __name__ == "__main__":
    run()
