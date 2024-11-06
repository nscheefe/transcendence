import graphene
import grpc
from main_service.protos.game_pb2_grpc import GameServiceStub
from main_service.protos.game_pb2 import GetGameRequest, CreateGameRequest

# Define the game type
class GameType(graphene.ObjectType):
    id = graphene.Int()

# Define the GraphQL query type
class Query(graphene.ObjectType):
    game = graphene.Field(GameType, id=graphene.Int(required=True))

    def resolve_game(self, info, id):
        # Connect to gRPC game service
        channel = grpc.insecure_channel('game_service:50051')  # Docker container service name
        client = GameServiceStub(channel)

        # Call the gRPC service
        request = GetGameRequest(id=id)
        response = client.GetGame(request)

        if response.id == 0:
            return None

        return GameType(
            id=response.id
        )

# Define the CreateGame mutation
class CreateGame(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    game = graphene.Field(GameType)

    def mutate(self, info, id):
        # Connect to gRPC game service
        channel = grpc.insecure_channel('game_service:50051')  # Docker container service name
        client = GameServiceStub(channel)

        # Call the gRPC service
        request = CreateGameRequest(id=id)
        response = client.CreateGame(request)

        return CreateGame(game=GameType(
            id=response.id
        ))

# Define the mutation type
class Mutation(graphene.ObjectType):
    create_game = CreateGame.Field()

# Update the schema to include the query and mutation
schema = graphene.Schema(query=Query, mutation=Mutation)