import grpc
import google
from django.utils import timezone
from game_service.protos import game_pb2_grpc, game_pb2
from .models import Game


class GameServiceHandler(game_pb2_grpc.GameServiceServicer):
    def __init__(self):
        pass

    def GetGame(self, request, context):
        try:
            # Fetch the game from the database
            game = Game.objects.get(id=request.game_id)
            response = game_pb2.Game(
                id=game.id,
                state=game.state,
                points_player_a=game.points_player_a,
                points_player_b=game.points_player_b,
                player_a_id=game.player_a_id,
                player_b_id=game.player_b_id,
                finished=game.finished,
                created_at=google.protobuf.timestamp_pb2.Timestamp(seconds=int(game.created_at.timestamp())),
                updated_at=google.protobuf.timestamp_pb2.Timestamp(seconds=int(game.updated_at.timestamp()))
            )
            return response
        except Game.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Game with ID {request.game_id} not found")
            return game_pb2.Game()  # Return empty Game proto on failure

    def CreateGame(self, request, context):
        try:
            # Create and save a new game entry
            game = Game(
                state=request.state,
                points_player_a=request.points_player_a,
                points_player_b=request.points_player_b,
                player_a_id=request.player_a_id,
                player_b_id=request.player_b_id,
                # Optional fields like "finished" default to False
                finished=request.finished or False,
            )
            game.save()
            game.refresh_from_db()

            # Build a proper gRPC response
            response = game_pb2.Game(
                id=game.id,
                state=game.state,
                points_player_a=game.points_player_a,
                points_player_b=game.points_player_b,
                player_a_id=game.player_a_id,
                player_b_id=game.player_b_id,
                finished=game.finished
            )
            if game.created_at:
                created_at = google.protobuf.timestamp_pb2.Timestamp()
                created_at.FromDatetime(game.created_at)
                response.created_at.CopyFrom(created_at)
            if game.updated_at:
                updated_at = google.protobuf.timestamp_pb2.Timestamp()
                updated_at.FromDatetime(game.updated_at)
                response.updated_at.CopyFrom(updated_at)

            return response
        except Exception as e:
            context.set_details(f"Error creating game: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return game_pb2.Game()

    def GetOngoingGames(self, request, context):
        try:
            # Query all ongoing (unfinished) games
            games = Game.objects.filter(finished=False)
            response = game_pb2.GetOngoingGamesResponse()

            for game in games:
                game_message = game_pb2.Game(
                    id=game.id,
                    state=game.state,
                    points_player_a=game.points_player_a,
                    points_player_b=game.points_player_b,
                    player_a_id=game.player_a_id,
                    player_b_id=game.player_b_id,
                    finished=game.finished,
                    created_at=google.protobuf.timestamp_pb2.Timestamp(seconds=int(game.created_at.timestamp())),
                    updated_at=google.protobuf.timestamp_pb2.Timestamp(seconds=int(game.updated_at.timestamp()))
                )
                response.games.append(game_message)
            return response
        except Exception as e:
            context.set_details(f"Error fetching ongoing games: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return game_pb2.GetOngoingGamesResponse()

    def StartGame(self, request, context):
        """
        Start a game and return WebSocket URL for real-time updates.
        """
        try:
            # Fetch the game from the database
            game = Game.objects.get(id=request.game_id)

            # If game is already finished, return an error
            if game.finished:
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                context.set_details("Game is already finished")
                return game_pb2.StartGameResponse()

            # Logic to "start" the game (you can add game-specific logic here)
            game.state = "active"
            game.save()

            # WebSocket URL for real-time updates
            websocket_url = f"ws://websocket_service/games/{game.id}"

            # Return success and WebSocket URL
            return game_pb2.StartGameResponse(
                success=True,
                websocket_url=websocket_url
            )
        except Game.DoesNotExist:
            # If the game doesn't exist, return an error
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Game with ID {request.game_id} not found")
            return game_pb2.StartGameResponse()

    def HandleGameFinished(self, request, context):
        """
        Update the game as finished with the information provided from WebSocket callback.
        """
        try:
            # Fetch the game from the database
            game = Game.objects.get(id=request.game_id)

            # Update game stats
            game.points_player_a = request.points_player_a
            game.points_player_b = request.points_player_b
            game.state = "finished"
            game.finished = True

            # Determine the winner and save it as part of the game's state
            if request.winner_player_id == game.player_a_id:
                game.state = "finished - Player A won"
            elif request.winner_player_id == game.player_b_id:
                game.state = "finished - Player B won"
            else:
                game.state = "finished - Draw"

            # Save updates to the database
            game.save()

            # Return empty response as acknowledgment
            return Empty()
        except Game.DoesNotExist:
            # If the game doesn't exist, return an error
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Game with ID {request.game_id} not found")
            return Empty()

    @classmethod
    def as_servicer(cls):
        return cls()
