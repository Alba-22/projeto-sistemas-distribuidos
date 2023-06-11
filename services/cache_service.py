import json
from utils.enums import Collection


class CacheService:

    _cache = {
        Collection.Clients.value: {},
        Collection.Products.value: {},
        Collection.Orders.value: {},
    }

    def put(self, collection: Collection, identifier: str, data: dict):
        self._cache[collection.value][identifier] = json.dumps(data)

    def delete(self, collection: Collection, identifier: str):
        try:
            del self._cache[collection.value][identifier]
            return True
        except KeyError:
            # Ao tentar acessar, caso não tenha, dá keyError
            return False

    def get(self, collection: Collection, identifier: str):
        try:
            value = self._cache[collection.value][identifier]
            return json.loads(value)
        except KeyError:
            # Ao tentar acessar, caso não tenha, dá keyError
            return None
