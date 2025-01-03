from datetime import datetime
import graphene
import grpc

# Importing gRPC stubs & request messages
from main_service.protos.game_pb2_grpc import GameServiceStub
from main_service.protos.game_pb2 import (
    GetGameRequest,
    GetOngoingGamesRequest,
    CreateGameRequest,
    StartGameRequest,
    GameFinishedRequest,
)

from main_service.protos.gameEvent_pb2_grpc import GameEventServiceStub
from main_service.protos.gameEvent_pb2 import (
    GetGameEventRequest,
    CreateGameEventRequest,
)

GRPC_TARGET = "game_service:50051"  # The gRPC service endpoint


# ---------------------------------------
# GraphQL Object Types
# ---------------------------------------

class GameType(graphene.ObjectType):
    id = graphene.Int()
    state = graphene.String()
    points_player_a = graphene.Int()
    points_player_b = graphene.Int()
    player_a_id = graphene.Int()
    player_b_id = graphene.Int()
    finished = graphene.Boolean()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()


class GameEventType(graphene.ObjectType):
    id = graphene.Int()
    game_id = graphene.Int()
    event_type = graphene.String()
    event_data = graphene.String()
    timestamp = graphene.DateTime()


# ---------------------------------------
# GraphQL Queries
# ---------------------------------------

class Query(graphene.ObjectType):
    game = graphene.Field(GameType, game_id=graphene.Int(required=True))
    ongoing_games = graphene.List(GameType)
    game_event = graphene.Field(GameEventType, game_event_id=graphene.Int(required=True))

    def resolve_game(self, info, game_id):
        """Fetch a specific game by its ID."""
        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                client = GameServiceStub(channel)
                request = GetGameRequest(game_id=game_id)
                response = client.GetGame(request)

                return GameType(
                    id=response.id,
                    state=response.state,
                    points_player_a=response.points_player_a,
                    points_player_b=response.points_player_b,
                    player_a_id=response.player_a_id,
                    player_b_id=response.player_b_id,
                    finished=response.finished,
                    created_at=datetime.fromtimestamp(response.created_at.seconds),
                    updated_at=datetime.fromtimestamp(response.updated_at.seconds),
                )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()}")

    def resolve_ongoing_games(self, info):
        """Fetch all ongoing games."""
        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                client = GameServiceStub(channel)
                request = GetOngoingGamesRequest()
                response = client.GetOngoingGames(request)

                return [
                    GameType(
                        id=game.id,
                        state=game.state,
                        points_player_a=game.points_player_a,
                        points_player_b=game.points_player_b,
                        player_a_id=game.player_a_id,
                        player_b_id=game.player_b_id,
                        finished=game.finished,
                        created_at=datetime.fromtimestamp(game.created_at.seconds),
                        updated_at=datetime.fromtimestamp(game.updated_at.seconds),
                    )
                    for game in response.games
                ]
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()}")

    def resolve_game_event(self, info, game_event_id):
        """Fetch a game event by its ID."""
        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                client = GameEventServiceStub(channel)
                request = GetGameEventRequest(game_event_id=game_event_id)
                response = client.GetGameEvent(request)

                return GameEventType(
                    id=response.id,
                    game_id=response.game_id,
                    event_type=response.event_type,
                    event_data=response.event_data,
                    timestamp=datetime.fromtimestamp(response.timestamp.seconds),
                )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()}")


# ---------------------------------------
# GraphQL Mutations
# ---------------------------------------

# Mutation for creating a game
class CreateGame(graphene.Mutation):
    class Arguments:
        state = graphene.String(required=True)
        points_player_a = graphene.Int(required=True)
        points_player_b = graphene.Int(required=True)
        player_a_id = graphene.Int(required=True)
        player_b_id = graphene.Int(required=True)

    game = graphene.Field(GameType)

    @staticmethod
    def mutate(root, info, state, points_player_a, points_player_b, player_a_id, player_b_id):
        """Create a new game."""
        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                client = GameServiceStub(channel)
                request = CreateGameRequest(
                    state=state,
                    points_player_a=points_player_a,
                    points_player_b=points_player_b,
                    player_a_id=player_a_id,
                    player_b_id=player_b_id,
                )
                response = client.CreateGame(request)

                return CreateGame(
                    game=GameType(
                        id=response.id,
                        state=response.state,
                        points_player_a=response.points_player_a,
                        points_player_b=response.points_player_b,
                        player_a_id=response.player_a_id,
                        player_b_id=response.player_b_id,
                        created_at=datetime.fromtimestamp(response.created_at.seconds),
                        updated_at=datetime.fromtimestamp(response.updated_at.seconds),
                    )
                )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()}")



# Mutation for creating a game event
class CreateGameEvent(graphene.Mutation):
    class Arguments:
        game_id = graphene.Int(required=True)
        event_type = graphene.String(required=True)
        event_data = graphene.String(required=True)

    game_event = graphene.Field(GameEventType)

    @staticmethod
    def mutate(root, info, game_id, event_type, event_data):
        """Create a new game event."""
        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                client = GameEventServiceStub(channel)
                request = CreateGameEventRequest(
                    game_id=game_id,
                    event_type=event_type,
                    event_data=event_data,
                )
                response = client.CreateGameEvent(request)

                return CreateGameEvent(
                    game_event=GameEventType(
                        id=response.id,
                        game_id=response.game_id,
                        event_type=response.event_type,
                        event_data=response.event_data,
                        timestamp=datetime.fromtimestamp(response.timestamp.seconds),
                    )
                )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()}")


# Mutation for starting a game
class StartGame(graphene.Mutation):
    class Arguments:
        game_id = graphene.Int(required=True)

    success = graphene.Boolean()
    websocket_url = graphene.String()

    @staticmethod
    def mutate(root, info, game_id):
        """Start a specific game."""
        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                client = GameServiceStub(channel)
                request = StartGameRequest(game_id=game_id)
                response = client.StartGame(request)

                return StartGame(
                    success=True,
                    websocket_url=response.websocket_url,
                )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()}")


# Register all mutations
class Mutation(graphene.ObjectType):
    create_game = CreateGame.Field()
    create_game_event = CreateGameEvent.Field()
    start_game = StartGame.Field()


# ---------------------------------------
# GraphQL Schema
# ---------------------------------------

schema = graphene.Schema(query=Query, mutation=Mutation)
