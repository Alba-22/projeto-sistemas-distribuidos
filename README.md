# Projeto Sistemas Distribuídos

Um sistema básico de simulação de um e-commerce simples para a disciplina GBC074 - Sistemas Distribuídos. O foco é fazer a comunicação entre diferentes processos por meio de gRPC e MQTT.

## Funcionalidades implementadas

- Comunicação entre OrderPortalClient e OrderPortalServer por gPRC
- Comunicação entre AdminPortalClient e AdminPortalServer por gPRC
- Comunicação entre o OrderPortalServer e AdminPortalServer por MQTT
- Múltiplas instâncias de AdminPortalServer e OrderPortalServer(desde que sejam inicializadas ao mesmo tempo) se comunicando por MQTT
- Múltiplos OrderPortalClient's podem se conectar a um mesmo OrderPortalServer
- Múltiplos AdminPortalClient's podem se conectar a um mesmo AdminPortalServer
- Script de testes

## Stack utilizada

Todo o projeto foi criado usando Python na versão 3.11.2.

Para implementar os conceitos de gRPC foram utilizadas as bibliotecas: `grpcio`, `grpcio-tools` e `protobuf`.
Já para implementar o modelo Pub/Sub por MQTT foi utilizado o `paho-mqtt`.

Outras bibliotecas usadas foram colocadas para questões de organização de projeto, typing, linter, etc.

## Documentação

### gRPC

O formato da mensagens para comunicação entre os clientes e servidores está definido no arquivo protobuf no caminho `proto/api.proto`.

```proto
syntax = "proto3";

message Client {
  // Client ID
  string CID = 1;
  // JSON string representing client data: at least a name
  string data = 2;
}

message Product {
  // Produto ID
  string PID = 1;
  // JSON string representing produto data: at least product name, price, and
  // quantity
  string data = 2;
}

message Order {
  // Order ID
  string OID = 1;
  // CLient ID
  string CID = 2;
  // JSON string representing at least array of PIDs, prices, and quantities
  string data = 3;
}

message Reply {
  // Error code: 0 for success
  int32 error = 1;
  // Error message, if error > 0
  optional string description = 2;
}

message ID {
  // generic ID for CID, PID and OID
  string ID = 1;
}

service AdminPortal {
  rpc CreateClient(Client) returns (Reply) {}
  rpc RetrieveClient(ID) returns (Client) {}
  rpc UpdateClient(Client) returns (Reply) {}
  rpc DeleteClient(ID) returns (Reply) {}
  rpc CreateProduct(Product) returns (Reply) {}
  rpc RetrieveProduct(ID) returns (Product) {}
  rpc UpdateProduct(Product) returns (Reply) {}
  rpc DeleteProduct(ID) returns (Reply) {}
}

service OrderPortal {
  rpc CreateOrder(Order) returns (Reply) {}
  rpc RetrieveOrder(ID) returns (Order) {}
  rpc UpdateOrder(Order) returns (Reply) {}
  rpc DeleteOrder(ID) returns (Reply) {}
  rpc RetrieveClientOrders(ID) returns (stream Order) {}
}
```

### MQTT

No projeto o MQTT é usado para fazer a comunicação entre as várias instâncias de AdminPortalServer e de OrderPortalServer.

Em cada instância, há uma variável do tipo dicionário que guarda os dados da aplicação em memória na seguinte estrutura:

```
hash_map = {
  "clients": {
    "CID": "data"
  },
  "products": {
    "PID": "data"
  },
  "orders": {
    "OID": "data"
  },
}
```

Nisso, no modelo Pub/Sub há 3 tópicos correspondentes às chaves do hash_map("clients", "products" e "orders") e cada processo do servidor escuta por mudanças publicadas nesses tópicos para alterar o próprio hash_map em memória.

As mensagens publicadas no broker MQTT seguem o seguinte formato:

```
{
  "op": str,
  "key": str,
  "data": dict,
}
```

em que:

- `op` pode assumir os seguintes valores: "ADD", "UPDATE" ou "DELETE"
- `key` corresponde ao CID, OID ou PID, a depender do tópico em que se está publicando
- `data` é um dicionário que terá o conteúdo a ser guardado para a key especificada naquele tóopico

A manipulação desse objeto que encapsula uma operação no broker está presente em `utils/on_receive_message.py` e em todas as referências ao método `publish` do MQTT.

## Rodando localmente

Clone o projeto

```bash
  git clone git@github.com:Alba-22/projeto-sistemas-distribuidos.git
```

Entre no diretório do projeto

```bash
  cd projeto-sistemas-distribuidos
```

Instale as dependências

```bash
  pip install -r requirements.txt
```

Inicie o mosquitto localmente, a porta padrão do projeto é a 1884

```bash
  mosquitto -p 1884
```

### Rodando os portais

Para todos as execuções, substitua {port} pelo número da porta que deseja rodar. Cada client deve especificar a porta do servidor que ele estará conectando. E cada servidor deve indicar em qual porta ele estará rodando. Múltiplos servidores não podem rodar na mesma porta, mas múltiplos clientes podem se conectar a mesma porta(desde que seja para o portal correspondete)

**Para rodar o cliente do portal de pedidos**

```bash
  python -m order.order_portal_client {port}
```

Ao início da execução, deve-se informar o CID.

**Para rodar o servidor do portal de pedidos**

```bash
  python -m order.order_portal_server {port}
```

**Para rodar o cliente do portal de administrador**

```bash
  python -m admin.admin_portal_client {port}
```

**Para rodar o servidor do portal de administrador**

```bash
  python -m admin.admin_portal_server {port}
```
