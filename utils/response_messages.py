from proto import api_pb2

def bad_request(message: str):
    return api_pb2.Reply(
        error=400,
        description=f"${message}"
    )

def not_found(message: str):
    return api_pb2.Reply(
        error=404,
        description=f"${message}"
    )

def internal_server_error(message: str):
    return api_pb2.Reply(
        error=500, description=f"{message}"
    )

def ok():
    return api_pb2.Reply(
        error=0
    )
