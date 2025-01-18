import time
from datetime import datetime

import grpc
import google
from game_service.protos import game_pb2_grpc, game_pb2
from google.protobuf.empty_pb2 import Empty
from .models import Game


class GameServiceHandler(game_pb2_grpc.GameServiceServicer):
    def __init__(self):
        self.game_ready_subscribers = {}
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

    def GetOnGoingGameByUser(self, request, context):
        try:
            # Fetch the game from the database
            game = (
                Game.objects.filter(player_a_id=request.user_id, finished=False).first() or
                Game.objects.filter(player_b_id=request.user_id, finished=False).first()
            )

            if not game:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"No game found for player ID {request.user_id}")
                return game_pb2.Game()

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
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching game for player ID {request.player_id}: {str(e)}")
            return game_pb2.Game()

    def CreateGame(self, request, context):
        try:
            # Check if there's an existing game for the user
            existing_game = (
                Game.objects.filter(
                    finished=False,
                    player_a_id=request.player_id
                ).first() or
                Game.objects.filter(
                    finished=False,
                    player_b_id=request.player_id
                ).first()
            )

            if existing_game:
                # If an unfinished game exists, return it
                response = game_pb2.Game(
                    id=existing_game.id,
                    state=existing_game.state,
                    points_player_a=existing_game.points_player_a,
                    points_player_b=existing_game.points_player_b,
                    player_a_id=existing_game.player_a_id,
                    player_b_id=existing_game.player_b_id,
                    finished=existing_game.finished,
                )
                if existing_game.created_at:
                    created_at = google.protobuf.timestamp_pb2.Timestamp()
                    created_at.FromDatetime(existing_game.created_at)
                    response.created_at.CopyFrom(created_at)
                if existing_game.updated_at:
                    updated_at = google.protobuf.timestamp_pb2.Timestamp()
                    updated_at.FromDatetime(existing_game.updated_at)
                    response.updated_at.CopyFrom(updated_at)

                return response

            # Check if an unfinished game without player_b exists
            open_game = Game.objects.filter(finished=False, player_b_id__isnull=True).first()
            if open_game:
                open_game.player_b_id = request.player_id
                open_game.state = "READY"
                open_game.updated_at = datetime.now()
                open_game.save()

                response = game_pb2.Game(
                    id=open_game.id,
                    state=open_game.state,
                    points_player_a=open_game.points_player_a,
                    points_player_b=open_game.points_player_b,
                    player_a_id=open_game.player_a_id,
                    player_b_id=open_game.player_b_id,
                    finished=open_game.finished,
                )
                if open_game.created_at:
                    created_at = google.protobuf.timestamp_pb2.Timestamp()
                    created_at.FromDatetime(open_game.created_at)
                    response.created_at.CopyFrom(created_at)
                if open_game.updated_at:
                    updated_at = google.protobuf.timestamp_pb2.Timestamp()
                    updated_at.FromDatetime(open_game.updated_at)
                    response.updated_at.CopyFrom(updated_at)

                return response

            # No existing game was found; create a new one
            new_game = Game(
                player_a_id=request.player_id,
                player_b_id= None,
                points_player_a=0,
                points_player_b=0,
                state = "WAITING",
                finished = False,
                created_at = datetime.now(),
                updated_at = datetime.now()
            )
            new_game.save()

            # Return the newly created game
            response = game_pb2.Game(
                id=new_game.id,
                state=new_game.state,
                points_player_a=new_game.points_player_a,
                points_player_b=new_game.points_player_b,
                player_a_id=new_game.player_a_id,
                player_b_id=new_game.player_b_id,
                finished=new_game.finished,
            )
            if new_game.created_at:
                created_at = google.protobuf.timestamp_pb2.Timestamp()
                created_at.FromDatetime(new_game.created_at)
                response.created_at.CopyFrom(created_at)
            if new_game.updated_at:
                updated_at = google.protobuf.timestamp_pb2.Timestamp()
                updated_at.FromDatetime(new_game.updated_at)
                response.updated_at.CopyFrom(updated_at)

            return response

        except Exception as e:
            # Handle errors and return gRPC error response
            context.set_details(f"Error creating or finding game: {str(e)}")
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

    def GameReady(self, request, context):
        """
        Server-Streaming RPC to notify clients when a game is "READY."
        Clients subscribe via GameReadyRequest containing the `game_id`.
        """

        # Extract game_id from the request
        game_id = request.game_id

        try:
            # Ensure the game exists in the database.
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Game with ID {game_id} not found")
            return

        # Notify client when the game's state transitions to "READY."
        # This is a **server-streaming RPC**, so we will stream updates to the client.
        try:
            # Simulate an async subscription
            while True:
                # Fetch the latest game state from the DB
                logging.debug("Fetching the latest state for the game with ID: %s", game.id)
                game.refresh_from_db()

                # Prepare debug message for the WebSocket client
                debug_message = f"Game ID {game.id}: state={game.state}"
                # Only send a notification if the game is ready
                #if game.state == "READY":
                response = game_pb2.Game(
                    id=game.id,
                    state=game.state,
                    points_player_a=game.points_player_a,
                    points_player_b=game.points_player_b,
                    player_a_id=game.player_a_id,
                    player_b_id=game.player_b_id,
                    finished=game.finished,
                    created_at=game_pb2.google_dot_protobuf_dot_timestamp__pb2.Timestamp(
                        seconds=int(game.created_at.timestamp())),
                    updated_at=game_pb2.google_dot_protobuf_dot_timestamp__pb2.Timestamp(
                        seconds=int(game.updated_at.timestamp())),
                )
                yield {
                    "debug": f"Game is READY. Notification sent. {debug_message}",
                    "data": response,
                }

                # After notification, break the loop as no more updates are needed
                logging.debug("Stopping stream after game state READY for game ID: %s", game.id)
                break

                # Send a "heartbeat" to keep the connection alive (optional)
                time.sleep(1)
        except Exception as e:
            # Handle issues such as database errors or network failures
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error monitoring game readiness: {str(e)}")
            return
        except Exception as e:
            # Handle issues such as database errors or network failures
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error monitoring game readiness: {str(e)}")
            return

    @classmethod
    def as_servicer(cls):
        return cls()
