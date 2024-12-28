import grpc
from concurrent import futures
from game_service.protos import game_pb2_grpc, game_pb2
from game_service.game.models import Game

class GameServiceHandler(game_pb2_grpc.GameServiceServicer):
    def __init__(self):
        pass

    def GetGame(self, request, context):
        try:
            game = Game.objects.get(id=request.id)
            return game_pb2.Game(
                id=game.id
            )
        except Game.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Game not found')
            return game_pb2.Game()

    def CreateGame(self, request, context):
        game = Game(
            id=request.id
        )
        game.save()
        return game_pb2.Game(
            id=game.id
        )

    def GetGames(self, request, context):
        games = Game.objects.all()
        return game_pb2.GameList(
            games=[game_pb2.Game(id=game.id) for game in games]
        )

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    game_service_handler = GameServiceHandler.as_servicer()
    game_pb2_grpc.add_GameServiceServicer_to_server(game_service_handler, server)