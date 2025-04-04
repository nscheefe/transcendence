from datetime import datetime
import asyncio
from asyncio.log import logger

import grpc.aio
import grpc
from graphql import GraphQLResolveInfo
from main_service.api.schema.objectTypes import query, mutation, subscription
from main_service.protos.gameEvent_pb2 import GetGameEventRequest, CreateGameEventRequest
from main_service.protos.gameEvent_pb2_grpc import GameEventServiceStub
from main_service.protos.game_pb2 import (
    GetGameRequest,
    GetOngoingGamesRequest,
    CreateGameRequest,
    CreateFriendGameRequest,
    UpdateGameStateRequest,
    StartGameRequest,
)
from main_service.protos.game_pb2_grpc import GameServiceStub
from main_service.protos.notification_pb2 import CreateNotificationRequest
from main_service.protos.notification_pb2_grpc import NotificationServiceStub
from main_service.protos.tournament_pb2 import (
    GetTournamentRoomRequest,
    CreateTournamentRoomRequest,
    ListTournamentRoomsRequest,
    ListTournamentUsersRequest,
    CreateTournamentUserRequest,
    UpdateTournamentUserRequest,
    ListTournamentGameMappingsRequest,
    CreateTournamentGameMappingRequest,
)
from main_service.protos.tournament_pb2_grpc import TournamentServiceStub

from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timedelta
import grpc
from graphql import GraphQLResolveInfo
from main_service.protos import chat_pb2, chat_pb2_grpc


from .userSchema import resolve_profile

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
    """Fetch a specific tournament by ID, including its users."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            # Fetch tournament details
            client = TournamentServiceStub(channel)
            request = GetTournamentRoomRequest(tournament_room_id=tournament_id)
            response = client.GetTournamentRoom(request)

            # Fetch tournament users
            users_request = ListTournamentUsersRequest(tournament_room_id=tournament_id)
            users_response = client.ListTournamentUsers(users_request)

            # Debug the structure of users_response
            print("Users Response:", users_response)

            # Adjust this based on the actual structure of the response
            if hasattr(users_response, "users"):
                user_list = users_response.users
            elif hasattr(users_response, "tournament_users"):
                user_list = users_response.tournament_users
            else:
                user_list = []

            # Map users to a list of dictionaries
            users = [
                {
                    "id": user.id,
                    "user_id": user.user_id,
                    "state": user.State,
                    "play_order": user.play_order,  # Handle missing fields gracefully
                    "games_played": user.games_played,
                    "created_at": datetime.fromtimestamp(user.created_at.seconds).isoformat(),
                    "updated_at": datetime.fromtimestamp(user.updated_at.seconds).isoformat()
                }
                for user in user_list
            ]

            # Return tournament details with users


            return {
                "id": response.id,
                "name": response.name,
                "is_active": response.is_active,
                "started": response.started,
                "chat_room_id": response.chat_room_id,
                "tournament_size": response.tournament_size,
                "start_time": datetime.fromtimestamp(response.start_time.seconds).isoformat() if response.HasField(
                    "start_time") else None,
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
                "updated_at": datetime.fromtimestamp(response.updated_at.seconds).isoformat(),
                "users": users
            }
    except Exception as e:
        print(f"Error fetching tournament or users: {str(e)}")
        raise e


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
                return []

            # Process the "tournament_rooms" data and format it for GraphQL response

            return [
                {
                    "id": tournament.id,
                    "name": tournament.name,
                    "is_active": tournament.is_active,
                    "started": tournament.started,
                    "chat_room_id":tournament.chat_room_id,
                    "tournament_size": tournament.tournament_size,
                    "start_time": datetime.fromtimestamp(
                        tournament.start_time.seconds).isoformat() if tournament.HasField(
                        "start_time") else None,
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


            if not tournament_game_mappings or not isinstance(tournament_game_mappings, list):
                return []  # Gracefully return an empty list when no games are found

            # Map each tournament_game_mapping to the GraphQL response format
            return [
                {
                    "id": game.id,
                    "game_id": game.game_id,
                    "tournament_id": game.tournament_room_id,
                    "created_at": datetime.fromtimestamp(game.created_at.seconds).isoformat(),
                    "updated_at": None,  # If `updated_at` is not provided
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
                    "state": user.State,
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
def resolve_create_tournament(_, info: GraphQLResolveInfo, name: str, tournament_size: int):
    """Create a new tournament with size and default start time."""
    print("create_tournament mutation called.")  # Debug: Confirm function is called
    logger.info("create_tournament mutation called.")

    # Ensure authentication if needed (similar to `resolve_start_chat_with_user`)
    current_user_id = info.context["request"].user_id
    if not current_user_id:
        raise Exception("Authentication required: user_id is missing")

    try:
        # Calculate the default start time as a datetime object
        default_start_time = datetime.utcnow() + timedelta(hours=1)
        print(f"Default start time calculated: {default_start_time}")  # Debug: Check calculated time

        # Convert default_start_time to a Protobuf Timestamp
        start_time_proto = Timestamp()
        start_time_proto.FromDatetime(default_start_time)
        print(f"Start time converted to Protobuf: {start_time_proto}")  # Debug: Check Protobuf timestamp

        print("Setting up chat service gRPC channel...")
        # Create the chat room using a synchronous gRPC channel
        with grpc.insecure_channel("chat_service:50051") as chat_channel:
            chat_stub = chat_pb2_grpc.ChatRoomControllerStub(chat_channel)

            # Create the chat room
            chat_request = chat_pb2.ChatRoomRequest(name=name, game_id=0)
            chat_response = chat_stub.Create(chat_request)
            print(f"Chat room created with ID: {chat_response.id}")  # Debug: Check chat creation response
            logger.info(f"Chat room created: {chat_response}")


        # Create the tournament room using another gRPC service
        print("Setting up tournament service gRPC channel...")
        with grpc.insecure_channel(GRPC_TARGET) as tournament_channel:
            tournament_stub = TournamentServiceStub(tournament_channel)

            # Create a tournament room request
            tournament_request = CreateTournamentRoomRequest(
                name=name,
                tournament_size=tournament_size,
                chat_room_id=chat_response.id,
                start_time=start_time_proto
            )

            # Call the tournament service to create the tournament room
            tournament_response = tournament_stub.CreateTournamentRoom(tournament_request)
            print(f"Tournament room created with ID: {tournament_response.id}")  # Debug
            logger.info(f"Tournament room created: {tournament_response}")

        # Format the response for GraphQL
        print("Formatting response for GraphQL...")
        return {
            "id": tournament_response.id,
            "name": tournament_response.name,
            "is_active": tournament_response.is_active,
            "chat_room_id": tournament_response.chat_room_id,
            "started": tournament_response.started,
            "tournament_size": tournament_response.tournament_size,
            "start_time": datetime.fromtimestamp(tournament_response.start_time.seconds).isoformat()
            if tournament_response.HasField("start_time") else None,
            "created_at": datetime.fromtimestamp(tournament_response.created_at.seconds).isoformat(),
            "updated_at": datetime.fromtimestamp(tournament_response.updated_at.seconds).isoformat(),
        }

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            logger.error(f"Tournament room already exists: {e}")
            return None
        else:
            print(f"gRPC Error: {e.details()}")
            logger.error(f"gRPC error: {e.details()}")
            raise Exception(f"gRPC error: {e.details()}")

    except Exception as e:
        print(f"Unexpected error in create_tournament: {str(e)}")
        logger.error(f"Unexpected error in create_tournament: {str(e)}")
        raise Exception(f"Error: {str(e)}")

@mutation.field("create_tournament_user")
def resolve_create_tournament_user(_, info: GraphQLResolveInfo, tournament_id: int, user_id: int):
    """Create a new user in a tournament."""
    try:
        chatChanel = grpc.insecure_channel("chat_service:50051")
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)
            chatRoomuserClient = chat_pb2_grpc.ChatRoomUserControllerStub(chatChanel)
            tournamenRoom = resolve_tournament(_, info, tournament_id)
            chatUserRequest = chat_pb2.ChatRoomUserRequest(chat_room=tournamenRoom["chat_room_id"], user_id=user_id)
            chatUserResponse = chatRoomuserClient.Create(chatUserRequest)
            request = CreateTournamentUserRequest(
                tournament_room_id=tournament_id,
                user_id=user_id,  # Pass the user_id explicitly
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

@mutation.field("update_tournament_user")
def resolve_update_tournament_user(_, info: GraphQLResolveInfo, tournament_user_id: int, state: str):
    """Update a user in a tournament."""
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)
            request = UpdateTournamentUserRequest(
                tournament_user_id=tournament_user_id,
                state=state,
            )
            response = client.UpdateTournamentUser(request)

            return {
                "success": True,
                "user": {
                    "id": response.id,
                    "tournament_room_id": response.tournament_room_id,
                    "user_id": response.user_id,
                    "state": response.State,
                    "play_order": response.play_order,
                    "games_played": response.games_played,
                    "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
                    "updated_at": datetime.fromtimestamp(response.updated_at.seconds).isoformat(),
                }
            }
    except grpc.RpcError as e:
        # Handle gRPC errors and raise an appropriate exception
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
def resolve_create_tournament_game(_, info: GraphQLResolveInfo, tournament_id: int, user_id: int, opponent_id: int):
    """Creates a tournament game."""
    user = info.context["request"].user_id

    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = TournamentServiceStub(channel)
            clientGmae = GameServiceStub(channel)

            request = CreateFriendGameRequest(player_a=user, player_b=opponent_id)
            response = clientGmae.CreateFriendGame(request)

            request = CreateTournamentGameMappingRequest(
                game_id=response.id,
                tournament_room_id=tournament_id,
                user_id=user_id
            )
            response = client.CreateTournamentGameMapping(request)

            return {
                "id": response.id,
                "game_id": response.game_id,  # Replace with correct field
                "user_id": response.user_id,
                "tournament_id": response.tournament_room_id,  # Replace with correct field
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat(),
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()}")


@mutation.field("create_friend_game")
def resolve_create_friend_game(_, info: GraphQLResolveInfo, player_a: int, player_b: int):
    """
    Create a game between two specific players.
    """
    user_id = info.context["request"].user_id
    user_chanel = grpc.insecure_channel("user_service:50051")
    chat_chanel = grpc.insecure_channel("chat_service:50051")

    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = GameServiceStub(channel)
            request = CreateFriendGameRequest(player_a=player_a, player_b=player_b)
            response = client.CreateFriendGame(request)
            notification_stub = NotificationServiceStub(user_chanel)
            chat_stub = chat_pb2_grpc.ChatRoomControllerStub(chat_chanel)

            profile = resolve_profile(_, info, user_id)
            profileb = resolve_profile(_, info, player_b)

            nickname = profile["nickname"]
            nicknamePlayerB = profileb["nickname"]
            notification_request = CreateNotificationRequest(
                user_id=player_b,
                message=f"User {nickname} sent you an Game invitation.",
                read=False,
                sent_at=datetime.utcnow()
            )
            notification_stub.CreateNotification(notification_request)
            chat_request = chat_pb2.ChatRoomRequest(
                    name= nickname +  " vs " + nicknamePlayerB,
                    game_id=response.id,
            )
            chatRoom = chat_stub.Create(chat_request)
            chatRoomUserStub = chat_pb2_grpc.ChatRoomUserControllerStub(chat_chanel)
            chatRoomUser_request = chat_pb2.ChatRoomUserRequest(chat_room=chatRoom.id, user_id=user_id)
            chatRoomUser_request_friend = chat_pb2.ChatRoomUserRequest(chat_room=chatRoom.id, user_id=player_b)

            chatRoomUserStub.Create(chatRoomUser_request)
            chatRoomUserStub.Create(chatRoomUser_request_friend)

            messagestub = chat_pb2_grpc.ChatRoomMessageControllerStub(chat_chanel)
            messagerequest = chat_pb2.ChatRoomMessageRequest(
                content = f"§GAME_INVITE§ Game ID:{response.id} {user_id}invited{player_b}",
                sender_id = user_id,
                chat_room = chatRoom.id,
            )
            messagestub.Create(messagerequest)

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


@mutation.field("update_game_state")
def resolve_update_game_state(_, info: GraphQLResolveInfo, game_id: int, state: str):
    """
    Update the state of a specific game.
    """
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            client = GameServiceStub(channel)
            request = UpdateGameStateRequest(id=game_id, state=state)
            response = client.UpdateGameState(request)

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


# ---------------------------------------
# Create the Executable Schema
# ---------------------------------------
resolver = [query, mutation, subscription]
