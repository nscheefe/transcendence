import graphene
import grpc
from main_service.protos.user_pb2_grpc import UserServiceStub
from main_service.protos.user_pb2 import GetUserRequest, CreateUserRequest, Permission, PermissionType

# Define the user type
class UserType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    secret = graphene.String()
    isAuth = graphene.Boolean()
    blocked = graphene.Boolean()
    permissions = graphene.List(graphene.String)

# Define the GraphQL query type
class Query(graphene.ObjectType):
    user = graphene.Field(UserType, id=graphene.Int(required=True))

    def resolve_user(self, info, id):
        # Connect to gRPC user service
        channel = grpc.insecure_channel('user_service:50051')  # Docker container service name
        client = UserServiceStub(channel)

        # Call the gRPC service
        request = GetUserRequest(id=id)
        response = client.GetUser(request)

        if response.id == 0:
            return None

        return UserType(
            id=response.id,
            name=response.name,
            secret=response.secret,
            isAuth=response.isAuth,
            blocked=response.blocked,
            permissions=response.permissions
        )

# Define the CreateUser mutation
class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        secret = graphene.String(required=True)
        permissions = graphene.List(graphene.String, required=True)
        isAuth = graphene.Boolean(required=True)
        blocked = graphene.Boolean(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, name, secret, permissions, isAuth, blocked):
        # Connect to gRPC user service
        channel = grpc.insecure_channel('user_service:50051')  # Docker container service name
        client = UserServiceStub(channel)

        # Prepare permissions
        grpc_permissions = [Permission(id=i, type=PermissionType.USER) for i in range(len(permissions))]

        # Call the gRPC service
        request = CreateUserRequest(
            name=name,
            secret=secret,
            permissions=grpc_permissions,
            isAuth=isAuth,
            blocked=blocked
        )
        response = client.CreateUser(request)

        return CreateUser(user=UserType(
            id=response.id,
            name=response.name,
            secret=response.secret,
            isAuth=response.isAuth,
            blocked=response.blocked,
            permissions=response.permissions
        ))

# Define the mutation type
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()

# Update the schema to include the query and mutation
schema = graphene.Schema(query=Query, mutation=Mutation)