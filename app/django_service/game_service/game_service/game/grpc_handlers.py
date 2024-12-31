from concurrent import futures
import grpc
from game_service.protos import gameEvent_pb2_grpc
from game_service.game.game_event_grpc_handler import GameEventServiceHandler
from game_service.protos import game_pb2_grpc
from game_service.game.game_grpc_handler import GameServiceHandler


def grpc_handlers(server):
    """
    Function to register gRPC service handlers for GameEvent and Game services.
    """

    # Register GameEvent Service Handler
    game_event_service_handler = GameEventServiceHandler.as_servicer()
    gameEvent_pb2_grpc.add_GameEventServiceServicer_to_server(game_event_service_handler, server)

    # Register Game Service Handler
    game_service_handler = GameServiceHandler.as_servicer()
    game_pb2_grpc.add_GameServiceServicer_to_server(game_service_handler, server)
