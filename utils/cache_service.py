from enum import Enum

class CacheCollection(Enum):
    Clients = "clients"
    Products = "products"
    Orders = "orders"

class CacheService:

    cache = {
        CacheCollection.Clients.value: {},
        CacheCollection.Products.value: {},
        CacheCollection.Orders.value: {},
    }

    def add(self, collection: CacheCollection, identifier: str, data):
        self.cache[collection.value][identifier] = data

    def delete(self, collection: CacheCollection, identifier: str):
        del self.cache[collection.value][identifier]
