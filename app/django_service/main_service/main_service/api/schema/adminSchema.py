import graphene
import grpc
from main_service.protos.admin_pb2_grpc import AdminServiceStub
from main_service.protos.admin_pb2 import GetAdminRequest, CreateAdminRequest

# Define the admin type
class AdminType(graphene.ObjectType):
    id = graphene.Int()

# Define the GraphQL query type
class Query(graphene.ObjectType):
    admin = graphene.Field(AdminType, id=graphene.Int(required=True))

    def resolve_admin(self, info, id):
        # Connect to gRPC admin service
        channel = grpc.insecure_channel('admin_service:50051')  # Docker container service name
        client = AdminServiceStub(channel)

        # Call the gRPC service
        request = GetAdminRequest(id=id)
        response = client.GetAdmin(request)

        if response.id == 0:
            return None

        return AdminType(
            id=response.id
        )

# Define the CreateAdmin mutation
class CreateAdmin(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    admin = graphene.Field(AdminType)

    def mutate(self, info, id):
        # Connect to gRPC admin service
        channel = grpc.insecure_channel('admin_service:50051')  # Docker container service name
        client = AdminServiceStub(channel)

        # Call the gRPC service
        request = CreateAdminRequest(id=id)
        response = client.CreateAdmin(request)

        return CreateAdmin(admin=AdminType(
            id=response.id
        ))

# Define the mutation type
class Mutation(graphene.ObjectType):
    create_admin = CreateAdmin.Field()

# Update the schema to include the query and mutation
schema = graphene.Schema(query=Query, mutation=Mutation)