import grpc
from django.db import IntegrityError
from user_service.protos import role_pb2_grpc, role_pb2
from user.models import Role

class RoleServiceHandler(role_pb2_grpc.RoleServiceServicer):
    def __init__(self):
        pass

    def GetRole(self, request, context):
        try:
            role = Role.objects.get(id=request.id)
            return role_pb2.Role(
                id=role.id,
                name=role.name
            )
        except Role.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Role not found')
            return role_pb2.Role()

    def CreateRole(self, request, context):
        try:
            role = Role(name=request.name)
            role.save()
            return role_pb2.Role(
                id=role.id,
                name=role.name
            )
        except IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('Role name already exists')
            return role_pb2.Role()

    def UpdateRole(self, request, context):
        try:
            role = Role.objects.get(id=request.id)
            role.name = request.name
            role.save()
            return role_pb2.Role(
                id=role.id,
                name=role.name
            )
        except Role.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Role not found')
            return role_pb2.Role()
        except IntegrityError:
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('Role name already exists')
            return role_pb2.Role()

    def DeleteRole(self, request, context):
        try:
            role = Role.objects.get(id=request.id)
            role.delete()
            return role_pb2.RoleDeleteResponse(
                success=True
            )
        except Role.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Role not found')
            return role_pb2.RoleDeleteResponse(
                success=False,
                message='Role not found'
            )

    @classmethod
    def as_servicer(cls):
        return cls()

