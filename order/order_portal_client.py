from __future__ import print_function

import logging

import grpc
import os



def run():
    # Stabilish connection to server
    # print("Will try to greet world ...")
    # with grpc.insecure_channel('localhost:50051') as channel:
    #     stub = helloworld_pb2_grpc.GreeterStub(channel)
    #     response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    # print("Greeter client received: " + response.message)

    cid = input("Digite o seu ID de Cliente: ")
    keep = True
    while (keep):
        os.system('cls' if os.name == 'nt' else 'clear')
        option = get_menu_option(cid);
        if (option == "1"):
            print("1")
        elif (option == "2"):
            print("2")
        elif (option == "3"):
            print("3")
        elif (option == "4"):
            print("4")
        elif (option == "5"):
            print("5")
        elif (option == "6"):
            cid = input("Digite o ID de Cliente que deseja utilizar: ")
            print("ID alterado para: " + cid + "!")
            end_of_option()
        elif (option == "7"):
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

if __name__ == '__main__':
    logging.basicConfig()
    run()