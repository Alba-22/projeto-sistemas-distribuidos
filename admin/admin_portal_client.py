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
        clear_screen()
        option = get_menu_option()
        if option == "1":
            clear_screen()
            print("========================")
            print("> Adição de Novo Cliente")
            client_id = input("Digite o id do novo cliente: ")
            client_name = input("Digite o nome do cliente: ")
            result = stub.CreateClient(api_pb2.Client(CID=client_id, data=json.dumps({"name": client_name})))
            if result.error == 0:
                print("Cliente adicionado com sucesso!")
            else:
                print(f"Erro: {result.description}")
            end_of_option()
        elif option == "2":
            clear_screen()
            print("========================")
            print("> Obter Cliente")
            client_id = input("Digite o id cliente: ")
            result = stub.RetrieveClient(api_pb2.ID(ID=client_id))
            if len(result.CID) != 0:
                print(f"[-] ID: {result.CID}")
                data = json.loads(result.data)
                for key, value in data.items():
                    print(f"[-] {key}: {value}")
                    
            else:
                print(f"Erro: Não há nenhum cliente com o ID {client_id}")
            end_of_option()
        elif option == "3":
            clear_screen()
            print("========================")
            print("> Atualização de Cliente")
            client_id = input("Digite o id do cliente: ")
            client_name = input("Digite o novo nome do cliente: ")
            result = stub.UpdateClient(api_pb2.Client(CID=client_id, data=json.dumps({"name": client_name})))
            if result.error == 0:
                print("Cliente atualizado com sucesso!")
            else:
                print(f"Erro: {result.description}")
            end_of_option()
        elif option == "4":
            clear_screen()
            print("========================")
            print("> Deleção de Cliente")
            client_id = input("Digite o id do cliente: ")
            result = stub.DeleteClient(api_pb2.ID(ID=client_id))
            if result.error == 0:
                print("Cliente deletado com sucesso!")
            else:
                print(f"Erro: {result.description}")
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

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    logging.basicConfig()
    run()
