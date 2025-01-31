import grpc
from concurrent import futures
from google.protobuf import empty_pb2
from datetime import datetime

# Import auto-generated gRPC and proto files
from game_service.protos import tournament_pb2
from game_service.protos import tournament_pb2_grpc
from django.utils.timezone import make_aware

# Import Django models
from .models import TournamentRoom, TournamentUser, TournamentGameMapping
from django.db.models import Max

# Implementation of the TournamentService Servicer
class TournamentServiceHandler:

    def __init__(self):
        pass
    # Tournament Room RPCs

    def GetTournamentRoom(self, request, context):
        try:
            room = TournamentRoom.objects.get(id=request.tournament_room_id)
            response = tournament_pb2.TournamentRoom(
                id=room.id,
                name=room.name,
                is_active=room.is_active,
                tournament_size = room.tournament_size,
                chat_room_id=room.chat_room_id,
                started = room.started,
                start_time = room.start_time,
                created_at=datetime_to_proto(room.created_at),
                updated_at=datetime_to_proto(room.updated_at),
            )
            return response
        except TournamentRoom.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Tournament Room not found.")

    def ListTournamentRooms(self, request, context):
        rooms = TournamentRoom.objects.all()
        response = tournament_pb2.ListTournamentRoomsResponse(
            tournament_rooms=[
                tournament_pb2.TournamentRoom(
                    id=room.id,
                    name=room.name,
                    is_active=room.is_active,
                    tournament_size=room.tournament_size,
                    started=room.started,
                    start_time=room.start_time,
                    created_at=datetime_to_proto(room.created_at),
                    updated_at=datetime_to_proto(room.updated_at),
                )
                for room in rooms
            ]
        )
        return response

    def CreateTournamentRoom(self, request, context):
        from google.protobuf.timestamp_pb2 import Timestamp
        from datetime import datetime
        from django.utils.timezone import make_aware

        # Convert Protobuf Timestamp to Python datetime and make it timezone-aware
        start_time = make_aware(datetime.fromtimestamp(request.start_time.seconds))
        print("chromrequest id", request.chat_room_id)
        # Create the tournament room with additional fields: tournament_size and start_time
        room = TournamentRoom.objects.create(
            name=request.name,
            is_active=True,
            tournament_size=request.tournament_size,
            chat_room_id = request.chat_room_id,
            start_time=start_time
        )

        # Helper function to convert datetime to Protobuf Timestamp
        def datetime_to_proto(dt):
            if dt is None:
                return None
            timestamp = Timestamp()
            timestamp.FromDatetime(dt)
            return timestamp

        # Prepare the response, including the newly added fields
        response = tournament_pb2.TournamentRoom(
            id=room.id,
            name=room.name,
            is_active=room.is_active,
            chat_room_id= room.chat_room_id,
            tournament_size=room.tournament_size,  # Include tournament size
            start_time=datetime_to_proto(room.start_time),  # Ensure Protobuf Timestamp is used
            created_at=datetime_to_proto(room.created_at),
            updated_at=datetime_to_proto(room.updated_at),
        )
        return response

    def UpdateTournamentRoom(self, request, context):
        try:
            room = TournamentRoom.objects.get(id=request.tournament_room_id)
            room.name = request.name
            room.is_active = request.is_active
            room.save()
            response = tournament_pb2.TournamentRoom(
                id=room.id,
                name=room.name,
                is_active=room.is_active,
                tournament_size=room.tournament_size,
                started=room.started,
                start_time=room.start_time,
                created_at=datetime_to_proto(room.created_at),
                updated_at=datetime_to_proto(room.updated_at),
            )
            return response
        except TournamentRoom.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Tournament Room not found.")

    def DeleteTournamentRoom(self, request, context):
        try:
            room = TournamentRoom.objects.get(id=request.tournament_room_id)
            room.delete()
            return empty_pb2.Empty()
        except TournamentRoom.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Tournament Room not found.")

    # Tournament User RPCs
    def GetTournamentUser(self, request, context):
        try:
            user = TournamentUser.objects.get(id=request.tournament_user_id)
            response = tournament_pb2.TournamentUser(
                id=user.id,
                tournament_room_id=user.tournament_room_id,
                user_id=user.user_id,
                State=user.state,
                play_order=user.play_order,
                games_played=user.games_played,
                created_at=datetime_to_proto(user.created_at),
                updated_at=datetime_to_proto(user.updated_at),
            )
            return response
        except TournamentUser.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Tournament User not found.")

    def ListTournamentUsers(self, request, context):
        users = TournamentUser.objects.filter(tournament_room_id=request.tournament_room_id)
        response = tournament_pb2.ListTournamentUsersResponse(
            tournament_users=[
                tournament_pb2.TournamentUser(
                    id=user.id,
                    tournament_room_id=user.tournament_room_id,
                    user_id=user.user_id,
                    play_order=user.play_order,
                    State=user.state,
                    games_played=user.games_played,
                    created_at=datetime_to_proto(user.created_at),
                    updated_at=datetime_to_proto(user.updated_at),
                )
                for user in users
            ]
        )
        return response

    def CreateTournamentUser(self, request, context):
        try:
            # Fetch the highest play_order for the given tournament_room_id
            max_play_order = (
                    TournamentUser.objects.filter(tournament_room_id=request.tournament_room_id)
                    .aggregate(max_order=Max("play_order"))
                    .get("max_order") or 0  # Defaults to 0 if no users exist
            )

            # Assign the next play_order
            next_play_order = max_play_order + 1

            # Ensure uniqueness
            user, created = TournamentUser.objects.get_or_create(
                tournament_room_id=request.tournament_room_id,
                user_id=request.user_id,
                state="WAITING",
                defaults={"play_order": next_play_order},
            )

            if not created:
                context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    f"User {request.user_id} is already registered in Tournament Room {request.tournament_room_id}."
                )

            # Construct and return only the `TournamentUser` Protobuf object
            return tournament_pb2.TournamentUser(
                id=user.id,
                tournament_room_id=user.tournament_room_id,
                State=user.state,
                user_id=user.user_id,
                play_order=user.play_order,
                games_played=user.games_played,
                created_at=datetime_to_proto(user.created_at),
                updated_at=datetime_to_proto(user.updated_at),
            )

        except Exception as e:
            # Return an internal error message if something fails
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to create tournament user: {str(e)}")

    def UpdateTournamentUser(self, request, context):
        try:
            user = TournamentUser.objects.get(id=request.tournament_user_id)
            if request.play_order is not None and request.play_order != 0:
                user.play_order = request.play_order

            if request.games_played is not None and request.games_played != 0:
                user.games_played = request.games_played

            if request.state is not None:
                user.state = request.state

            user.save()
            response = tournament_pb2.TournamentUser(
                id=user.id,
                tournament_room_id=user.tournament_room_id,
                user_id=user.user_id,
                State=user.state,
                play_order=user.play_order,
                games_played=user.games_played,
                created_at=datetime_to_proto(user.created_at),
                updated_at=datetime_to_proto(user.updated_at),
            )
            return response
        except TournamentUser.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Tournament User not found.")

    def DeleteTournamentUser(self, request, context):
        try:
            user = TournamentUser.objects.get(id=request.tournament_user_id)
            user.delete()
            return empty_pb2.Empty()
        except TournamentUser.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Tournament User not found.")

    # Tournament Game Mapping RPCs
    def GetTournamentGameMapping(self, request, context):
        try:
            mapping = TournamentGameMapping.objects.get(id=request.tournament_game_mapping_id)
            response = tournament_pb2.TournamentGameMapping(
                id=mapping.id,
                tournament_room_id=mapping.tournament_room_id,
                game_id=mapping.game_id,
                user_id=mapping.user_id,
                created_at=datetime_to_proto(mapping.created_at),
            )
            return response
        except TournamentGameMapping.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Tournament Game Mapping not found.")

    def ListTournamentGameMappings(self, request, context):
        mappings = TournamentGameMapping.objects.filter(tournament_room_id=request.tournament_room_id)
        response = tournament_pb2.ListTournamentGameMappingsResponse(
            tournament_game_mappings=[
                tournament_pb2.TournamentGameMapping(
                    id=mapping.id,
                    tournament_room_id=mapping.tournament_room_id,
                    game_id=mapping.game_id,
                    user_id=mapping.user_id,
                    created_at=datetime_to_proto(mapping.created_at),
                )
                for mapping in mappings
            ]
        )
        return response

    def CreateTournamentGameMapping(self, request, context):
        mapping = TournamentGameMapping.objects.create(
            tournament_room_id=request.tournament_room_id,
            game_id=request.game_id,
            user_id=request.user_id,
        )
        response = tournament_pb2.TournamentGameMapping(
            id=mapping.id,
            tournament_room_id=mapping.tournament_room_id,
            game_id=mapping.game_id,
            user_id=mapping.user_id,
            created_at=datetime_to_proto(mapping.created_at),
        )
        return response

    def DeleteTournamentGameMapping(self, request, context):
        try:
            mapping = TournamentGameMapping.objects.get(id=request.tournament_game_mapping_id)
            mapping.delete()
            return empty_pb2.Empty()
        except TournamentGameMapping.DoesNotExist:
            context.abort(grpc.StatusCode.NOT_FOUND, "Tournament Game Mapping not found.")

    @classmethod
    def as_servicer(cls):
        return cls()

    # Utility function to convert datetime to protobuf timestamp

def datetime_to_proto(dt):
    timestamp = tournament_pb2.google_dot_protobuf_dot_timestamp__pb2.Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp
