import inspect
from typing import AsyncIterable

from datetime import datetime
import graphene
import grpc
import asyncio
from rx import Observable
# Importing gRPC stubs & request messages
from main_service.protos.game_pb2_grpc import GameServiceStub
from main_service.protos.game_pb2 import (
    GetGameRequest,
    GetOngoingGamesRequest,
    CreateGameRequest,
    StartGameRequest,
    GameFinishedRequest,
    GameReadyRequest,
)
from channels_graphql_ws import GraphqlWsConsumer

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
    hello = graphene.String()

    def resolve_hello(root, info):
        return "Hello, World!"
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
    """Defines the CreateGame mutation."""

    # Fields (output of the mutation)
    game = graphene.Field(lambda: GameType)  # The field to return the created/updated game

    class Arguments:
        """Any arguments required for this mutation."""
        player_id = graphene.ID(required=True)  # Example argument, could vary based on your logic

    @staticmethod
    def mutate(root, info, player_id):
        try:
            # Your mutation logic here, e.g., gRPC call
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                client = GameServiceStub(channel)
                request = CreateGameRequest(
                    player_id=info.context.user_id,  # Or player_id if passed in arguments
                )
                response = client.CreateGame(request)

                # Return the mutation response
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








class GameReadyType(graphene.ObjectType):
    id = graphene.Int()


import graphene
import channels_graphql_ws


class PingSubscription(channels_graphql_ws.Subscription):
    response = graphene.String()  # Define the output field for the subscription.

    @staticmethod
    def subscribe(root, info):
        """
        A simple subscription handler that subscribes all clients to the same group.
        """
        return ["ping_group"]  # All clients subscribe to the same group.

    @staticmethod
    def publish(payload, info):
        """
        Publish the payload to the subscribers.
        """
        return PingSubscription(response=payload["message"])  # Return the response field.

    @classmethod
    async def send_ping(cls):
        """
        Broadcast a message to all subscribers in the 'ping_group'.
        """
        await cls.broadcast_async(
            group="ping_group",  # All subscribers of the group receive the message.
            payload={"message": "pong"},  # Message content.
        )






# Example usage of PingSubscription in the root subscription schema
class Subscription(graphene.ObjectType):
    """GraphQL Subscription Root."""
    ping = PingSubscription.Field()





# Register all mutations
class Mutation(graphene.ObjectType):
    create_game = CreateGame.Field()
    create_game_event = CreateGameEvent.Field()
    start_game = StartGame.Field()



# ---------------------------------------
# GraphQL Schema
# ---------------------------------------

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
