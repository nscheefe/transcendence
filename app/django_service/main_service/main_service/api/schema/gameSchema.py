from graphql import GraphQLResolveInfo
from datetime import datetime
import grpc
from main_service.protos.game_pb2_grpc import GameServiceStub
from main_service.protos.tournament_pb2_grpc import TournamentServiceStub
from main_service.protos.game_pb2 import (
    GetGameRequest,
    GetOngoingGamesRequest,
    CreateGameRequest,
    StartGameRequest,
)
from main_service.protos.tournament_pb2 import (
    GetTournamentRoomRequest,
    ListTournamentRoomsResponse,
    CreateTournamentRoomRequest,
ListTournamentRoomsRequest,
    GetTournamentUserRequest,
    ListTournamentUsersRequest,
    CreateTournamentUserRequest,
    ListTournamentGameMappingsRequest,
    CreateTournamentGameMappingRequest,
)

from main_service.protos.gameEvent_pb2_grpc import GameEventServiceStub
from main_service.protos.gameEvent_pb2 import GetGameEventRequest, CreateGameEventRequest
from main_service.api.schema.objectTypes import query, mutation, subscription  # Shared objects

GRPC_TARGET = "game_service:50051"  # The gRPC service endpoint

# ---------------------------------------
# Type Definitions (SDL)
# ---------------------------------------

# ---------------------------------------
# Resolver Implementations
# ---------------------------------------

@query.field("hello")
def resolve_hello(_, info: GraphQLResolveInfo):
    return "Hello, World!"


@query.field("game")
def resolve_game(_, info: GraphQLResolveInfo, game_id: int):
    """Fetch a specific game by its ID."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = GameServiceStub(channel)
            request = GetGameRequest(game_id=game_id)
            response = client.GetGame(request)

            return {
                "id": response.id,
                "state": response.state,
                "points_player_a": response.points_player_a,
                "points_player_b": response.points_player_b,
                "player_a_id": response.player_a_id,
                "player_b_id": response.player_b_id,
                "finished": response.finished,
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
                "updated_at": datetime.fromtimestamp(response.updated_at.seconds).isoformat(),
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")


@query.field("tournament")
def resolve_tournament(_, info: GraphQLResolveInfo, tournament_id: int):
    """Fetch a specific tournament by ID."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)
            request = GetTournamentRoomRequest(tournament_room_id=tournament_id)
            response = client.GetTournamentRoom(request)

            return {
                "id": response.id,
                "name": response.name,
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
                "updated_at": datetime.fromtimestamp(response.updated_at.seconds).isoformat()
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")

@query.field("tournaments")
def resolve_tournaments(_, info: GraphQLResolveInfo):
    """Fetch all tournaments."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)

            # Create an empty request object
            request = ListTournamentRoomsRequest()

            # Fetch the response from gRPC
            response = client.ListTournamentRooms(request)

            # Access the "tournament_rooms" field instead of "tournaments"
            tournament_rooms = getattr(response, "tournament_rooms", None)

            if not tournament_rooms:  # Handle invalid structure
                raise Exception(f"Unexpected response structure: {response}")

            # Process the "tournament_rooms" data and format it for GraphQL response
            return [
                {
                    "id": tournament.id,
                    "name": tournament.name,
                    "created_at": datetime.fromtimestamp(tournament.created_at.seconds).isoformat(),
                    "updated_at": datetime.fromtimestamp(tournament.updated_at.seconds).isoformat(),
                }
                for tournament in tournament_rooms
            ]
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")


@query.field("tournament_games")
def resolve_tournament_games(_, info: GraphQLResolveInfo, tournament_id: int):
    """Fetch all games mapped to a tournament."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)
            request = ListTournamentGameMappingsRequest(tournament_room_id=tournament_id)
            response = client.ListTournamentGameMappings(request)

            # Fetch the correct field from the response
            tournament_game_mappings = getattr(response, "tournament_game_mappings", None)

            if not tournament_game_mappings:  # If the expected field doesn't exist, handle gracefully
                raise Exception(f"Unexpected response structure: {response}")

            # Map each tournament_game_mapping to the GraphQL response format
            return [
                {
                    "id": game.id,
                    "game_id": game.game_id,
                    "tournament_id": game.tournament_room_id,
                    "created_at": datetime.fromtimestamp(game.created_at.seconds).isoformat(),
                    "updated_at": None,  # If `updated_at` does not exist, handle gracefully
                }
                for game in tournament_game_mappings
            ]
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")

@query.field("ongoing_games")
def resolve_ongoing_games(_, info: GraphQLResolveInfo):
    """Fetch all ongoing games."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = GameServiceStub(channel)
            request = GetOngoingGamesRequest()
            response = client.GetOngoingGames(request)

            return [
                {
                    "id": game.id,
                    "state": game.state,
                    "points_player_a": game.points_player_a,
                    "points_player_b": game.points_player_b,
                    "player_a_id": game.player_a_id,
                    "player_b_id": game.player_b_id,
                    "finished": game.finished,
                    "created_at": datetime.fromtimestamp(game.created_at.seconds).isoformat(),
                    "updated_at": datetime.fromtimestamp(game.updated_at.seconds).isoformat(),
                }
                for game in response.games
            ]
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")

@query.field("tournament_users")
def resolve_tournament_users(_, info: GraphQLResolveInfo, tournament_id: int):
    """Fetch all users of a tournament."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)
            request = ListTournamentUsersRequest(tournament_room_id=tournament_id)
            response = client.ListTournamentUsers(request)

            # Fetch the correct field from the gRPC response
            tournament_users = getattr(response, "tournament_users", None)

            if not tournament_users:  # Handle missing field in response
                raise Exception(f"Unexpected response structure: {response}")

            # Map each user to the GraphQL response format
            return [
                {
                    "id": user.id,
                    "user_id": user.user_id,  # Assuming `user_id` maps to FK User
                    "tournament_id": user.tournament_room_id,  # Maps directly to tournament FK
                    "created_at": datetime.fromtimestamp(user.created_at.seconds).isoformat(),
                    "updated_at": None,  # Add updated_at if your response doesn't have it
                }
                for user in tournament_users
            ]
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")


@query.field("game_event")
def resolve_game_event(_, info: GraphQLResolveInfo, game_event_id: int):
    """Fetch a game event by its ID."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = GameEventServiceStub(channel)
            request = GetGameEventRequest(game_event_id=game_event_id)
            response = client.GetGameEvent(request)

            return {
                "id": response.id,
                "game_id": response.game_id,
                "event_type": response.event_type,
                "event_data": response.event_data,
                "timestamp": datetime.fromtimestamp(response.timestamp.seconds).isoformat(),
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")  # Removed extra lines

@mutation.field("create_tournament")
def resolve_create_tournament(_, info: GraphQLResolveInfo, name: str):
    """Create a new tournament."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)
            request = CreateTournamentRoomRequest(name=name)
            response = client.CreateTournamentRoom(request)

            return {
                # Removed "description" from returned output
                "name": response.name,
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
                "updated_at": datetime.fromtimestamp(response.updated_at.seconds).isoformat(),
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")

@mutation.field("create_tournament_user")
def resolve_create_tournament_user(_, info: GraphQLResolveInfo, tournament_id: int, user_id: int):
    """Create a new user in a tournament.""" #@Todo this is wrong impolemented
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)
            request = CreateTournamentUserRequest(
                tournament_room_id=tournament_id,
                user_id=user_id,  # Pass the user_id explicitly
                play_order=1  # Or any default order
            )
            response = client.CreateTournamentUser(request)

            return {
                "success": True,
                "user": {
                    "id": response.id,
                    "tournament_room_id": response.tournament_room_id,  # Correct field based on proto
                    "user_id": response.user_id,
                    "play_order": response.play_order,
                    "games_played": response.games_played,
                    "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
                    "updated_at": datetime.fromtimestamp(response.updated_at.seconds).isoformat(),
                }
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")

@mutation.field("create_game")
def resolve_create_game(_, info: GraphQLResolveInfo):
    """Create a game."""
    try:
        # Get user ID from the request context
        user_id = info.context["request"].user_id
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = GameServiceStub(channel)
            # Pass the resolved user_id to the game creation request
            request = CreateGameRequest(player_id=user_id)
            response = client.CreateGame(request)

            return {
                "id": response.id,
                "state": response.state,
                "points_player_a": response.points_player_a,
                "points_player_b": response.points_player_b,
                "player_a_id": response.player_a_id,
                "player_b_id": response.player_b_id,
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
                "updated_at": datetime.fromtimestamp(response.updated_at.seconds).isoformat(),
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")



@mutation.field("create_game_event")
def resolve_create_game_event(_, info: GraphQLResolveInfo, game_id: int, event_type: str, event_data: str):
    """Create a game event."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = GameEventServiceStub(channel)
            request = CreateGameEventRequest(game_id=game_id, event_type=event_type, event_data=event_data)
            response = client.CreateGameEvent(request)

            return {
                "id": response.id,
                "game_id": response.game_id,
                "event_type": response.event_type,
                "event_data": response.event_data,
                "timestamp": datetime.fromtimestamp(response.timestamp.seconds).isoformat(),
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")


@mutation.field("start_game")
def resolve_start_game(_, info: GraphQLResolveInfo, game_id: int):
    """Start a game."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = GameServiceStub(channel)
            request = StartGameRequest(game_id=game_id)
            response = client.StartGame(request)

            return {"success": True, "websocket_url": response.websocket_url}
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")

@mutation.field("create_tournament_game")
def resolve_create_tournament_game(_, info: GraphQLResolveInfo, game_id: int, tournament_id: int, user_id: int):
    """Creates a tournament game."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)

            # Send the gRPC request to create the tournament game
            request = CreateTournamentGameMappingRequest(
                game_id=game_id,
                tournament_room_id=tournament_id,
                user_id=user_id
            )
            response = client.CreateTournamentGameMapping(request)

            # Map the response fields to the GraphQL schema
            return {
                "id": response.id,
                "game_id": response.game_id,  # Replace with correct field
                "tournament_id": response.tournament_room_id,  # Replace with correct field
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")



# ---------------------------------------
# Create the Executable Schema
# ---------------------------------------
resolver = [query, mutation, subscription]
