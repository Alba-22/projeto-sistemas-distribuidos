from enum import Enum

class Collection(Enum):
    Clients = "Clients"
    Products = "Products"
    Orders = "Orders"

class Operation(Enum):
    Add = "Add"
    Update = "Update"
    Delete = "Delete"
    Get = "Get"
