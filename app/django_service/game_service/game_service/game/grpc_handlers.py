from concurrent import futures
import grpc

# Import the necessary gRPC modules
from game_service.protos import gameEvent_pb2_grpc
from game_service.game.game_event_grpc_handler import GameEventServiceHandler
from game_service.protos import game_pb2_grpc
from game_service.game.game_grpc_handler import GameServiceHandler
from game_service.protos import tournament_pb2_grpc  # Import the tournament gRPC module
from game_service.game.game_tournament_grpc_handler import TournamentServiceHandler  # Import your handler


def grpc_handlers(server):
    """
    Function to register gRPC service handlers for GameEvent, Game, and Tournament services.
    """

    # Register GameEvent Service Handler
    game_event_service_handler = GameEventServiceHandler.as_servicer()
    gameEvent_pb2_grpc.add_GameEventServiceServicer_to_server(game_event_service_handler, server)

    # Register Game Service Handler
    game_service_handler = GameServiceHandler.as_servicer()
    game_pb2_grpc.add_GameServiceServicer_to_server(game_service_handler, server)

    # Register Game Tournament Service Handler
    game_tournament_service_handler = TournamentServiceHandler.as_servicer()
    tournament_pb2_grpc.add_TournamentServiceServicer_to_server(game_tournament_service_handler, server)
