import graphene
import grpc
from main_service.protos.stat_pb2_grpc import StatServiceStub
from main_service.protos.stat_pb2 import GetStatRequest, CreateStatRequest

# Define the stat type
class StatType(graphene.ObjectType):
    id = graphene.Int()

# Define the GraphQL query type
class Query(graphene.ObjectType):
    stat = graphene.Field(StatType, id=graphene.Int(required=True))

    def resolve_stat(self, info, id):
        # Connect to gRPC stat service
        channel = grpc.insecure_channel('stat_service:50051')  # Docker container service name
        client = StatServiceStub(channel)

        # Call the gRPC service
        request = GetStatRequest(id=id)
        response = client.GetStat(request)

        if response.id == 0:
            return None

        return StatType(
            id=response.id
        )

# Define the CreateStat mutation
class CreateStat(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    stat = graphene.Field(StatType)

    def mutate(self, info, id):
        # Connect to gRPC stat service
        channel = grpc.insecure_channel('stat_service:50051')  # Docker container service name
        client = StatServiceStub(channel)

        # Call the gRPC service
        request = CreateStatRequest(id=id)
        response = client.CreateStat(request)

        return CreateStat(stat=StatType(
            id=response.id
        ))

# Define the mutation type
class Mutation(graphene.ObjectType):
    create_stat = CreateStat.Field()

# Update the schema to include the query and mutation
schema = graphene.Schema(query=Query, mutation=Mutation)