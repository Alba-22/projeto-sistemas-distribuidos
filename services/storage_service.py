import json
import sys
from socket import socket as s
import threading
from typing import Collection, Optional

from pysyncobj import SyncObj, replicated
import lmdb

from utils.enums import Operation, Collection
from utils.socket_helper import message_to_socket, operation_from_socket

class StorageService(SyncObj):
    def __init__(self, socket_port: int, self_address: str, partner_addresses: list[str]):
        super(StorageService, self).__init__(self_address, partner_addresses)
        self.db_path = f"db_{socket_port}"

    @replicated
    def insert(self, identifier: str, data: str):
        print("INSERTING IN DB")
        with lmdb.open(self.db_path, map_size=50000000, writemap=True) as db:
            with db.begin(write=True) as transaction:
                transaction.put(identifier.encode(), data.encode())

    def get_by_id(self, identifier: str) -> Optional[dict]:
        print("GETTING FROM DB")
        try:
            with lmdb.open(self.db_path, map_size=50000000, writemap=True) as db:
                with db.begin(write=True) as transaction:
                    result = transaction.get(identifier.encode())
                    print(f"DB: {result}")
                    if result is None:
                        return None
                    return json.loads(result.decode())
        except:
            return None

    def get_all_by_collection(self, collection: Collection) -> list[dict]:
        items = []
        with lmdb.open(self.db_path, map_size=50000000, writemap=True) as db:
            with db.begin(write=True) as transaction:
                cursor = transaction.cursor()
                for item_key, item_value in iter(cursor):
                    if collection.value in item_key.decode():
                        items.append(json.loads(item_value.decode()))
        return items

    @replicated
    def update(self, identifier: str, data: str):
        print("UPDATED IN DB")
        with lmdb.open(self.db_path, map_size=50000000, writemap=True) as db:
            with db.begin(write=True) as transaction:
                transaction.put(identifier.encode(), data.encode())

    @replicated
    def delete(self, identifier: str):
        print("DELETED FROM DB")
        with lmdb.open(self.db_path, map_size=50000000, writemap=True) as db:
            with db.begin(write=True) as transaction:
                transaction.delete(identifier.encode())

class StorageSetup():

    def __init__(self, args):
        if args == 1:
            self.socket_port = 20001
            self.replic = StorageService(
                self.socket_port, "localhost:30001", ["localhost:30002", "localhost:30003"]
            )
        if args == 2:
            self.socket_port = 20002
            self.replic = StorageService(
                self.socket_port, "localhost:30002", ["localhost:30001", "localhost:30003"]
            )
        if args == 3:
            self.socket_port = 20003
            self.replic = StorageService(
                self.socket_port, "localhost:30003", ["localhost:30001", "localhost:30002"]
            )
        if args == 4:
            self.socket_port = 20004
            self.replic = StorageService(
                self.socket_port, "localhost:30004", ["localhost:30005", "localhost:30006"]
            )
        if args == 5:
            self.socket_port = 20005
            self.replic = StorageService(
                self.socket_port, "localhost:30005", ["localhost:30004", "localhost:30006"]
            )
        if args == 6:
            self.socket_port = 20006
            self.replic = StorageService(
                self.socket_port, "localhost:30006", ["localhost:30004", "localhost:30005"]
            )

    def start_socket(self):
        socket = s()
        socket.bind(("localhost", self.socket_port))
        socket.listen(30)

        while True:
            connection, address = socket.accept()
            threading.Thread(target=self.controller, args=(connection, address)).start()

    def controller(self, connection: s, address):
        print("Connected to ", address)
        while True:
            collection, operation, identifier, data = operation_from_socket(connection)
            result = self.process_message(collection, operation, identifier, data)
            print(f"Storage Controller: {result}")
            message_to_socket(connection, result)

    def process_message(self, collection: Collection, operation: Operation, identifier: str, data):
        print("Processing Message")
        if operation == Operation.Add:
            self.replic.insert(identifier, data)
            return {}
        elif operation == Operation.Get:
            client = self.replic.get_by_id(identifier)
            return client
        elif operation == Operation.Update:
            self.replic.update(identifier, data)
            return {}
        elif operation == Operation.Delete:
            self.replic.delete(identifier)
            return {}
        elif operation == Operation.List:
            return self.replic.get_all_by_collection(collection)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(-1)

    arg = int(sys.argv[1])

    if arg not in [1, 2, 3, 4, 5, 6]:
        print("Valor do argumento deve ser de 1 a 6")
    else:
        replica = StorageSetup(arg)
        replica.start_socket()
