import grpc
from django.db import IntegrityError
from user_service.protos import permission_pb2_grpc, permission_pb2
from user.models import Permission

class PermissionServiceHandler(permission_pb2_grpc.PermissionServiceServicer):
    def __init__(self):
        pass

    def GetPermission(self, request, context):
        try:
            permission = Permission.objects.get(id=request.id)
            return permission_pb2.Permission(
                id=permission.id,
                name=permission.name,
                description=permission.description
            )
        except Permission.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Permission not found')
            return permission_pb2.Permission()

    def CreatePermission(self, request, context):
        try:
            permission = Permission(name=request.name, description=request.description)
            permission.save()
            return permission_pb2.Permission(
                id=permission.id,
                name=permission.name,
                description=permission.description
            )
        except IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('Permission name already exists')
            return permission_pb2.Permission()

    def UpdatePermission(self, request, context):
        try:
            permission = Permission.objects.get(id=request.id)
            permission.name = request.name
            permission.description = request.description
            permission.save()
            return permission_pb2.Permission(
                id=permission.id,
                name=permission.name,
                description=permission.description
            )
        except Permission.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Permission not found')
            return permission_pb2.Permission()
        except IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('Permission name already exists')
            return permission_pb2.Permission()

    def DeletePermission(self, request, context):
        try:
            permission = Permission.objects.get(id=request.id)
            permission.delete()
            return permission_pb2.PermissionDeleteResponse(
                success=True
            )
        except Permission.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Permission not found')
            return permission_pb2.PermissionDeleteResponse(
                success=False,
                message='Permission not found'
            )

    @classmethod
    def as_servicer(cls):
        return cls()

