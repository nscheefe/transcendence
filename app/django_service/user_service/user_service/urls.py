# python
from user_service.user.grpc_handlers import UserServiceHandler
from .protos import user_pb2_grpc

urlpatterns = [
]

def grpc_handlers(server):
    user_service_handler = UserServiceHandler.as_servicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_service_handler, server)