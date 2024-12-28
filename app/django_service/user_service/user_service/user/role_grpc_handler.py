import grpc
from django.db import IntegrityError
from user_service.protos import role_pb2_grpc, role_pb2
from user.models import Role


class RoleServiceHandler(role_pb2_grpc.RoleServiceServicer):
    def __init__(self):
        pass

    def CreateRole(self, request, context):
        """
        Create a new role by its name.
        """
        try:
            # Create a new role object
            role = Role(name=request.name)
            role.save()

            # Return the newly created role as a protobuf message
            return role_pb2.Role(
                id=role.id,
                name=role.name
            )
        except IntegrityError:
            # Handle unique constraint for the role name
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details('Role name already exists')
            return role_pb2.Role()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to create role: {str(e)}')
            return role_pb2.Role()

    def GetRoleById(self, request, context):
        """
        Retrieve a role by its ID.
        """
        try:
            # Retrieve the role by ID
            role = Role.objects.get(id=request.id)

            # Return the role as a protobuf message
            return role_pb2.Role(
                id=role.id,
                name=role.name
            )
        except Role.DoesNotExist:
            # Handle case where the role does not exist
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Role not found')
            return role_pb2.Role()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f'Failed to retrieve role: {str(e)}')
            return role_pb2.Role()

    @classmethod
    def as_servicer(cls):
        """
        Helper function for registering the servicer with the gRPC server.
        """
        return cls()
