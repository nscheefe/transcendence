import google
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
        try:
            user = User(
                id= request.id,
                name=request.name,
                mail=request.mail,
                blocked=request.blocked,
                role_id=request.role_id,
                last_login_ip=request.last_login_ip or ""  # Default empty string for optional field
            )
            user.save()
            user.refresh_from_db()
            response = user_pb2.User(
                id=user.id,
                name=user.name,
                mail=user.mail,
                blocked=user.blocked,
                role_id=user.role_id,
                last_login_ip=user.last_login_ip,
            )
            if user.created_at:
                created_at = google.protobuf.timestamp_pb2.Timestamp()
                created_at.FromDatetime(user.created_at)
                response.created_at.CopyFrom(created_at)
            if user.updated_at:
                updated_at = google.protobuf.timestamp_pb2.Timestamp()
                updated_at.FromDatetime(user.updated_at)
                response.updated_at.CopyFrom(updated_at)

            return response

        except Exception as e:
            context.set_details(f"Error creating user: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return user_pb2.User()

    @classmethod
    def as_servicer(cls):
        return cls()

