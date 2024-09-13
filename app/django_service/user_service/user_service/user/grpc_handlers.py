# python
import grpc
from concurrent import futures
from user_service.protos import user_pb2_grpc, user_pb2
from user.models import User, Permission

class UserServiceHandler(user_pb2_grpc.UserServiceServicer):
    def __init__(self):
        pass

    def GetUser(self, request, context):
        try:
            user = User.objects.get(id=request.id)
            return user_pb2.User(
                id=user.id,
                name=user.name,
                secret=user.secret,
                isAuth=user.isAuth,
                blocked=user.blocked,
                permissions=[user_pb2.Permission(id=perm.id, type=perm.type) for perm in user.permissions.all()]
            )
        except User.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return user_pb2.User()

    def CreateUser(self, request, context):
        user = User(
            name=request.name,
            secret=request.secret,
            isAuth=request.isAuth,
            blocked=request.blocked
        )
        user.save()
        for perm in request.permissions:
            permission = Permission(id=perm.id, type=perm.type, user=user)
            permission.save()
        return user_pb2.User(
            id=user.id,
            name=user.name,
            secret=user.secret,
            isAuth=user.isAuth,
            blocked=user.blocked,
            permissions=[user_pb2.Permission(id=perm.id, type=perm.type) for perm in user.permissions.all()]
        )

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    user_service_handler = UserServiceHandler.as_servicer()
    user_pb2_grpc.add_UserServiceServicer_to_server(user_service_handler, server)