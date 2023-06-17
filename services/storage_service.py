import sys
from pysyncobj import SyncObj, SyncObjConf, replicated
import leveldb
import socket as s

from utils.enums import Collection, Operation
from utils.socket_helper import retrieve_from_socket

class StorageService(SyncObj):
    def __init__(self, self_address: str, partner_addresses: list[str]):
        config = SyncObjConf(dynamicMembershipChange=True)
        super(StorageService, self).__init__(self_address, partner_addresses, config)
        self.dbClients = leveldb.LevelDB("./db/db-clients")

    @replicated
    def insert_client(self, cid: str, data: str):
        # Inserir identificador de tipo(c, p, o)
        self.dbClients.Put(cid.encode(), data.encode())

    def get_client_by_id(self, cid: str):
        try:
            print("AAA")
            client = self.dbClients.Get(cid.encode())
            print(client)
            print(type(client))
            print("BBB")
            return client
        except:
            return None

class StorageSetup():

    def __init__(self, args):
        if args == 1:
            self.socket_port = 20001
            self.replic = StorageService("localhost:30001", ["localhost:30002", "localhost:30003"])
        if args == 2:
            self.socket_port = 20002
            self.replic = StorageService("localhost:30002", ["localhost:30001", "localhost:30003"])
        if args == 3:
            self.socket_port = 20003
            self.replic = StorageService("localhost:30003", ["localhost:30001", "localhost:30002"])

    def start_socket(self):
        socket = s.socket()
        socket.bind(("localhost", self.socket_port))
        socket.listen(10)

        while True:
            connection, address = socket.accept()
            print("Connected to ", address)
            with connection:
                collection, operation, identifier, data = retrieve_from_socket(
                    connection.recv(1024),
                )
                result = self.process_message(collection, operation, identifier, data)
                if result:
                    print("Request Successful")
                    connection.send("True".encode())
                else:
                    print("Request Unsuccessful")
                    connection.send("False".encode())
                connection.close()

    def process_message(self, collection: Collection, operation: Operation, identifier: str, data):
        if collection == Collection.Clients and operation == Operation.Add:
            self.replic.insert_client(identifier, data)
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(-1)

    arg = int(sys.argv[1])

    if arg != 1 and arg != 2 and arg != 3:
        print("Valor do argumento deve ser 1, 2 ou 3")
    else:
        replica = StorageSetup(arg)
        replica.start_socket()
