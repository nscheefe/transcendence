import graphene
import grpc
from main_service.protos.auth_pb2_grpc import AuthServiceStub
from main_service.protos.auth_pb2 import GetAuthRequest, CreateAuthRequest

# Define the auth type
class AuthType(graphene.ObjectType):
    id = graphene.Int()

# Define the GraphQL query type
class Query(graphene.ObjectType):
    auth = graphene.Field(AuthType, id=graphene.Int(required=True))

    def resolve_auth(self, info, id):
        # Connect to gRPC auth service
        channel = grpc.insecure_channel('auth_service:50051')  # Docker container service name
        client = AuthServiceStub(channel)

        # Call the gRPC service
        request = GetAuthRequest(id=id)
        response = client.GetAuth(request)

        if response.id == 0:
            return None

        return AuthType(
            id=response.id
        )

# Define the CreateAuth mutation
class CreateAuth(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    auth = graphene.Field(AuthType)

    def mutate(self, info, id):
        # Connect to gRPC auth service
        channel = grpc.insecure_channel('auth_service:50051')  # Docker container service name
        client = AuthServiceStub(channel)

        # Call the gRPC service
        request = CreateAuthRequest(id=id)
        response = client.CreateAuth(request)

        return CreateAuth(auth=AuthType(
            id=response.id
        ))

# Define the mutation type
class Mutation(graphene.ObjectType):
    create_auth = CreateAuth.Field()

# Update the schema to include the query and mutation
schema = graphene.Schema(query=Query, mutation=Mutation)