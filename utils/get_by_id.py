import json


def get_client_by_id(hash_map: dict, client_id: str):
    clients = hash_map["clients"]
    for key in clients.keys():
        if key == client_id:
            return json.loads(clients[key])
    return None


def get_order_by_id(hash_map: dict, order_id: str):
    orders = hash_map["orders"]
    for key in orders:
        if key == order_id:
            return json.loads(orders[key])
    return None


def get_product_by_id(hash_map: dict, product_id: str):
    products = hash_map["products"]
    for key in products.keys():
        if key == product_id:
            return json.loads(products[key])
    return None
