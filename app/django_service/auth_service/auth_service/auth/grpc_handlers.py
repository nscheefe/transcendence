import grpc
from concurrent import futures
from auth_service.protos import auth_pb2_grpc, auth_pb2
from auth_service.auth.models import Auth

class AuthServiceHandler(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        pass

    def GetAuth(self, request, context):
        try:
            auth = Auth.objects.get(id=request.id)
            return auth_pb2.Auth(
                id=auth.id
            )
        except Auth.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Auth not found')
            return auth_pb2.Auth()

    def CreateAuth(self, request, context):
        auth = Auth(
            id=request.id
        )
        auth.save()
        return auth_pb2.Auth(
            id=auth.id
        )

    def GetAuths(self, request, context):
        auths = Auth.objects.all()
        return auth_pb2.AuthList(
            auths=[auth_pb2.Auth(id=auth.id) for auth in auths]
        )

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    auth_service_handler = AuthServiceHandler.as_servicer()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(auth_service_handler, server)