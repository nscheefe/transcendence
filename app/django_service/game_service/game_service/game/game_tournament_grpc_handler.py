import grpc
from concurrent import futures
from google.protobuf import empty_pb2
from datetime import datetime

# Import auto-generated gRPC and proto files
from game_service.protos import tournament_pb2
from game_service.protos import tournament_pb2_grpc

# Import Django models
from .models import TournamentRoom, TournamentUser, TournamentGameMapping


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
                    created_at=datetime_to_proto(room.created_at),
                    updated_at=datetime_to_proto(room.updated_at),
                )
                for room in rooms
            ]
        )
        return response

    def CreateTournamentRoom(self, request, context):
        room = TournamentRoom.objects.create(name=request.name, is_active=True)
        response = tournament_pb2.TournamentRoom(
            id=room.id,
            name=room.name,
            is_active=room.is_active,
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
            # Ensure uniqueness: Check if user already exists in the tournament room
            user, created = TournamentUser.objects.get_or_create(
                tournament_room_id=request.tournament_room_id,
                user_id=request.user_id,
                defaults={
                    "play_order": request.play_order
                }
            )

            if not created:
                context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    f"User {request.user_id} is already registered in Tournament Room {request.tournament_room_id}."
                )

            # Construct the response
            response = tournament_pb2.TournamentUser(
                id=user.id,
                tournament_room_id=user.tournament_room_id,
                user_id=user.user_id,
                play_order=user.play_order,
                games_played=user.games_played,
                created_at=datetime_to_proto(user.created_at),
                updated_at=datetime_to_proto(user.updated_at),
            )
            return response

        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, f"Failed to create tournament user: {str(e)}")

    def UpdateTournamentUser(self, request, context):
        try:
            user = TournamentUser.objects.get(id=request.tournament_user_id)
            user.play_order = request.play_order
            user.games_played = request.games_played
            user.save()
            response = tournament_pb2.TournamentUser(
                id=user.id,
                tournament_room_id=user.tournament_room_id,
                user_id=user.user_id,
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
