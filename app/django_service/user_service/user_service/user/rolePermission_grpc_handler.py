
import grpc
from user_service.protos import rolePermission_pb2_grpc, rolePermission_pb2
from user.models import RolePermission

class RolePermissionServiceHandler(rolePermission_pb2_grpc.RolePermissionServiceServicer):
    def __init__(self):
        pass

    def GetRolePermission(self, request, context):
        try:
            role_permission = RolePermission.objects.get(role_id=request.role_id, permission_id=request.permission_id)
            return rolePermission_pb2.RolePermission(
                role_id=role_permission.role.id,
                permission_id=role_permission.permission.id
            )
        except RolePermission.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('RolePermission not found')
            return rolePermission_pb2.RolePermission()

    def CreateRolePermission(self, request, context):
        role_permission = RolePermission(
            role_id=request.role_id,
            permission_id=request.permission_id
        )
        role_permission.save()
        return rolePermission_pb2.RolePermission(
            role_id=role_permission.role.id,
            permission_id=role_permission.permission.id
        )

    def DeleteRolePermission(self, request, context):
        try:
            role_permission = RolePermission.objects.get(role_id=request.role_id, permission_id=request.permission_id)
            role_permission.delete()
            return rolePermission_pb2.RolePermissionDeleteResponse(
                success=True
            )
        except RolePermission.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('RolePermission not found')
            return rolePermission_pb2.RolePermissionDeleteResponse(
                success=False,
                message='RolePermission not found'
            )

    @classmethod
    def as_servicer(cls):
        return cls()

