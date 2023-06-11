from pysyncobj import SyncObj, SyncObjConf, replicated
import leveldb

from utils.enums import Collection, Operation

class StorageService(SyncObj):
    def __init__(self, self_address: str, partner_addresses: list[str]):
        config = SyncObjConf(dynamicMembershipChange=True)
        super(StorageService, self).__init__(self_address, partner_addresses, config)
        self.dbClients = leveldb.LevelDB("./db/db-clients")


    def receive_message(self, collection: Collection, operation: Operation, identifier: str, data):
        if collection == Collection.Clients and operation == Operation.Add:
            self.insert_client(identifier, data)
        return True

    @replicated
    def insert_client(self, cid: str, data: str):
        self.dbClients.Put(cid.encode(), data.encode())

    @replicated
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
