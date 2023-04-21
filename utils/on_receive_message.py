import json


def show_database(hash_map):
    print("> CLIENTES")
    for key in hash_map["clients"].keys():
        print(f"{key} -> {hash_map['clients'][key]}")
    print("> PRODUTOS")
    for key in hash_map["products"].keys():
        print(f"{key} -> {hash_map['products'][key]}")
    print("> PEDIDOS")
    for key in hash_map["orders"].keys():
        print(f"{key} -> {hash_map['orders'][key]}")


def on_receive_message(hash_map: dict, msg: str):
    print(f"[TÓPICO = {msg.topic}] Mensagem recebida: {msg.payload.decode()}")
    result = json.loads(msg.payload.decode())
    if result["op"] == "ADD":
        hash_map[msg.topic][result["key"]] = result["data"]
    elif result["op"] == "UPDATE":
        hash_map[msg.topic][result["key"]] = result["data"]
    elif result["op"] == "DELETE":
        del hash_map[msg.topic][result["key"]]

    show_database(hash_map)
