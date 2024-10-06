import grpc
from django.utils import timezone
from user_service.protos import user_pb2_grpc, user_pb2
from user.models import User

class UserServiceHandler(user_pb2_grpc.UserServiceServicer):
    def __init__(self):
        pass

    def GetUser(self, request, context):
        try:
            user = User.objects.get(id=request.id)
            return user_pb2.User(
                id=user.id,
                name=user.name,
                mail=user.mail,
                isAuth=user.isAuth,
                blocked=user.blocked,
                created_at=google.protobuf.timestamp_pb2.Timestamp(seconds=int(user.created_at.timestamp())),
                updated_at=google.protobuf.timestamp_pb2.Timestamp(seconds=int(user.updated_at.timestamp())),
                role_id=user.role_id,
                last_login=google.protobuf.timestamp_pb2.Timestamp(seconds=int(user.last_login.timestamp())) if user.last_login else None,
                last_login_ip=user.last_login_ip
            )
        except User.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return user_pb2.User()

    def CreateUser(self, request, context):
        user = User(
            name=request.name,
            mail=request.mail,
            isAuth=request.isAuth,
            blocked=request.blocked,
            role_id=request.role_id,
            last_login_ip=request.last_login_ip
        )
        # Assuming last_login and created_at/updated_at are handled automatically or not required at creation
        user.save()
        return user_pb2.User(
            id=user.id,
            name=user.name,
            mail=user.mail,
            isAuth=user.isAuth,
            blocked=user.blocked,
            role_id=user.role_id,
            last_login_ip=user.last_login_ip
            # created_at and updated_at can be returned similarly to last_login if needed
        )

    @classmethod
    def as_servicer(cls):
        return cls()

