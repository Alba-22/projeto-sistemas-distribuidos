from __future__ import print_function

import json
import logging
import os
import sys

import grpc

from proto import api_pb2, api_pb2_grpc


def run():
    # Check port
    if len(sys.argv) == 1:
        print("É necessário informar a porta que o servidor irá rodar")
        return
    port = sys.argv[1]
    try:
        int(port)
    except:
        print("O valor passado para a porta é inválido")
        return

    # Stabilish connection to server
    print("Conectando ao servidor...")

    try:
        channel = grpc.insecure_channel(f"localhost:{port}")
        stub = api_pb2_grpc.OrderPortalStub(channel)
    except:
        print(
            "Ocorreu um erro ao conectar ao servidor! Verifique se a porta está correta!"
        )
        return

    cid = input("Digite o seu ID de Cliente: ")
    keep = True
    while keep:
        os.system("cls" if os.name == "nt" else "clear")
        option = get_menu_option(cid)
        if option == "1":
            clear_screen()
            print("========================")
            print("> Criar novo pedido")
            order_id = input("Digite o ID do pedido: ")
            data = []
            will_update_products = input("Deseja adicionar produtos ao pedido? [S/N] ")
            if will_update_products == "S":
                product_index = 1
                print(f"Digite os dados do {product_index}o produto:")
                while True:
                    product_id = input("Digite o ID do produto: ")
                    product_quantity = input("Digite a quantidade que deseja comprar: ")
                    data.append({"id": product_id, "quantity": product_quantity})
                    keep_updating_products = input(
                        "Deseja adicionar mais um pedido? [S/N]"
                    )
                    if keep_updating_products == "N":
                        break
            result = stub.CreateOrder(
                api_pb2.Order(OID=order_id, CID=cid, data=json.dumps(data))
            )
            if result.error == 0:
                print("Pedido criado com sucesso!")
            else:
                print(f"Erro: {result.description}")
            end_of_option()

        elif option == "2":
            clear_screen()
            print("========================")
            print("> Obter dados do pedido")
            order_id = input("Digite o ID do pedido: ")
            result = stub.RetrieveOrder(api_pb2.ID(ID=order_id))
            if result.OID == 0:
                print("Não há nenhum pedido com o ID digitado")
            data = json.loads(result.data)
            if not isinstance(data["products"], list):
                print("Ocorreu um erro")
            elif len(data) == 0:
                print("O pedido ainda não possui nenhum produto adicionado")
            else:
                print("--------------------------------")
                print(f"Produtos do pedido {order_id}: ")
                print("--------------------------------")
                for product in data["products"]:
                    for key, value in product.items():
                        print(f"[-] {key}: {value}")
                    print("--------------------------------")
            end_of_option()
        elif option == "3":
            clear_screen()
            print("========================")
            print("> Atualizar Pedido")
            order_id = input("Digite o ID do pedido: ")
            data = []
            will_update_products = input(
                "Deseja alterar algum produto do pedido? [S/N] "
            )
            if will_update_products == "S":
                while True:
                    product_id = input("Digite o ID do produto: ")
                    product_quantity = input(
                        "Digite a nova quantidade[0 = deletar produto]: "
                    )
                    data.append({"id": product_id, "quantity": product_quantity})
                    keep_updating_products = input(
                        "Deseja alterar mais um pedido? [S/N]"
                    )
                    if keep_updating_products == "N":
                        break
            result = stub.UpdateOrder(
                api_pb2.Order(OID=order_id, CID=cid, data=json.dumps(data))
            )
            if result.error == 0:
                print("Pedido alterado com sucesso!")
            else:
                print(f"Erro: {result.description}")
            end_of_option()
        elif option == "4":
            clear_screen()
            print("========================")
            print("> Deletar pedido")
            order_id = input("Digite o ID do pedido: ")
            result = stub.DeleteOrder(api_pb2.ID(ID=order_id))
            if result.error == 0:
                print("Pedido deletado com sucesso!")
            else:
                print(f"Erro: {result.description}")
            end_of_option()
        elif option == "5":
            clear_screen()
            print("========================")
            print("> Meus pedidos")
            result = stub.RetrieveClientOrders(api_pb2.ID(ID=cid))
            has_orders = False
            for order in result:
                has_orders = True
                data = json.loads(order.data)
                print(f"PEDIDO {order.OID}")
                for product in data["products"]:
                    print(
                        f"[{product['PID']}] {product['name']}(x{product['quantity']}) - ${product['price']}"
                    )
                print("--------------------------------")
            if not has_orders:
                print(f"Não há nenhum pedido para o cliente de ID {cid}")

            end_of_option()

        elif option == "6":
            clear_screen()
            cid = input("Digite o ID de Cliente que deseja utilizar: ")
            print("ID alterado para: " + cid + "!")
            end_of_option()
        elif option == "7":
            print("Saindo...")
            end_of_option()
            keep = False
        else:
            print("Opção Inválida")
            end_of_option()


def get_menu_option(cid):
    print("====== MENU ======")
    print("ID do Cliente: " + cid)
    print("==================")
    print("[1] Criar Pedido")
    print("[2] Obter Pedido")
    print("[3] Atualizar Pedido")
    print("[4] Deletar Pedido")
    print("[5] Ver Meus Pedidos")
    print("[6] Trocar de Usuário")
    print("[7] Sair")
    option = input("[-] Escolha: ")

    return option


def end_of_option():
    input("Pressione qualquer tecla para continuar!")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    logging.basicConfig()
    run()
