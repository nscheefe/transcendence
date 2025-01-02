
import grpc
import google
from game_service.protos import gameEvent_pb2_grpc, gameEvent_pb2
from .models import GameEvent, Game


class GameEventServiceHandler(gameEvent_pb2_grpc.GameEventServiceServicer):
    """
    Implementation of the GameEvent gRPC service
    """

    def __init__(self):
        pass

    def GetGameEvent(self, request, context):
        """
        Retrieve a GameEvent by its ID.
        """
        try:
            # Attempt to fetch the GameEvent by ID
            game_event = GameEvent.objects.get(id=request.game_event_id)

            response = gameEvent_pb2.GameEvent(
                id=game_event.id,
                game_id=game_event.game.id,
                event_type=game_event.event_type,
                event_data=game_event.event_data,
                timestamp=google.protobuf.timestamp_pb2.Timestamp(seconds=int(game_event.timestamp.timestamp())),
            )
            return response
        except GameEvent.DoesNotExist:
            # If GameEvent is not found, return NOT_FOUND error
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"GameEvent with ID {request.game_event_id} not found")
            return gameEvent_pb2.GameEvent()  # Return empty GameEvent on failure

    def CreateGameEvent(self, request, context):
        """
        Create a new GameEvent entry.
        """
        try:
            # Validate that the related game exists
            try:
                game = Game.objects.get(id=request.game_id)
            except Game.DoesNotExist:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Game with ID {request.game_id} not found")
                return gameEvent_pb2.GameEvent()

            # Create and save the GameEvent
            game_event = GameEvent(
                game=game,
                event_type=request.event_type,
                event_data=request.event_data,
                timestamp=request.timestamp.ToDatetime(),  # Convert protobuf Timestamp to Django datetime
            )
            game_event.save()

            # Build the response object
            response = gameEvent_pb2.GameEvent(
                id=game_event.id,
                game_id=game_event.game.id,
                event_type=game_event.event_type,
                event_data=game_event.event_data,
                timestamp=google.protobuf.timestamp_pb2.Timestamp(seconds=int(game_event.timestamp.timestamp())),
            )
            return response
        except Exception as e:
            # Handle any unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating GameEvent: {str(e)}")
            return gameEvent_pb2.GameEvent()

    @classmethod
    def as_servicer(cls):
        """
        Class method to use this handler as a servicer.
        """
        return cls()
