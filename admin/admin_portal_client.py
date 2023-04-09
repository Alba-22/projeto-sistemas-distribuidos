from __future__ import print_function

import logging
import os
import sys

import grpc

from proto import api_pb2, api_pb2_grpc


def run():
    # Stabilish connection to server
    print("Conectando ao servidor...")
    # TODO: Tratamento de exceção @octo
    channel = grpc.insecure_channel("localhost:50051")
    stub = api_pb2_grpc.AdminPortalStub(channel)
    # stub.CreateClient(api_pb2.Client(CID=1, data=""))
    stub.RetrieveClient(api_pb2.ID(ID=4))

    # with grpc.insecure_channel('localhost:50055') as channel:
    #     stub = api_pb2_grpc.AdminPortalStub(channel)
    #     response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    # print("Greeter client received: " + response.message)

    keep = True
    while keep:
        os.system("cls" if os.name == "nt" else "clear")
        option = get_menu_option()
        if option == "1":
            print(option)
            stub.CreateClient(api_pb2.Client(CID=1))
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
