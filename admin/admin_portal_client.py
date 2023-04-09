from __future__ import print_function

import logging
import os
import json
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
        stub = api_pb2_grpc.AdminPortalStub(channel)
    except:
        print("Ocorreu um erro ao conectar ao servidor! Verifique se a porta está correta!")
        return

    keep = True
    while keep:
        os.system("cls" if os.name == "nt" else "clear")
        option = get_menu_option()
        if option == "1":
            print("========================")
            print("> Adição de Novo Cliente")
            client_id = input("Digite o id do novo cliente: ")
            client_name = input("Digite o nome do cliente: ")
            result = stub.CreateClient(api_pb2.Client(CID=client_id, data=json.dumps({"name": client_name})))
            if result.error == 0:
                print("Cliente adicionado com sucesso!")
            else:
                print(f"Ocorreu um erro: {result.description}")
            end_of_option()
        elif option == "2":
            print(option)
            end_of_option()
        elif option == "3":
            print(option)
            end_of_option()
        elif option == "4":
            print(option)
            end_of_option()
        elif option == "5":
            print(option)
            end_of_option()
        elif option == "6":
            print(option)
            end_of_option()
        elif option == "7":
            print(option)
            end_of_option()
        elif option == "8":
            print(option)
            end_of_option()
        elif option == "9":
            print("Saindo...")
            end_of_option()
            keep = False
        else:
            print("Opção Inválida")
            end_of_option()


def get_menu_option():
    print("====== MENU ======")
    print("> Clientes")
    print("[1] Criar Cliente")
    print("[2] Obter Cliente")
    print("[3] Atualizar Cliente")
    print("[4] Deletar Cliente")
    print("> Produtos")
    print("[5] Criar Cliente")
    print("[6] Obter Cliente")
    print("[7] Atualizar Cliente")
    print("[8] Deletar Cliente")
    print("> Outros")
    print("[9] Sair")
    option = input("> Escolha: ")

    return option


def end_of_option():
    input("Pressione qualquer tecla para continuar!")


if __name__ == "__main__":
    logging.basicConfig()
    run()
