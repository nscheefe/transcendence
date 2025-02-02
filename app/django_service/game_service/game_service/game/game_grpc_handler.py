import logging
import time
from datetime import datetime, timedelta
from django.utils.timezone import now
import threading

import grpc
import google
from game_service.protos import game_pb2_grpc, game_pb2
from game_service.protos.stat_pb2 import (
    GetStatRequest,
    CreateStatRequest,
    GetStatsByUserIdRequest,
    CalculateStatsRequest,
)
from game_service.protos.stat_pb2_grpc import StatServiceStub
import game_service.protos.chat_pb2_grpc as chat_pb2_grpc
import game_service.protos.chat_pb2 as chat_pb2
import google.protobuf.timestamp_pb2
from google.protobuf.empty_pb2 import Empty
from .models import Game, TournamentGameMapping, TournamentUser, TournamentRoom

logger = logging.getLogger('game_service')


def monitor_disconnected_game(game_id):
    """
    Monitors a game with DISCONNECTED state. If the game remains in this state
    for more than 1 minute, it will mark the game as finished.
    """
    logger.debug(f"Monitoring game {game_id} for prolonged disconnection.")
    try:
        # Wait for 1 minute before checking the game's state
        threading.Event().wait(60)  # Wait for 60 seconds

        # Fetch the game
        game = Game.objects.get(id=game_id)

        # Check if the game is still in the "DISCONNECTED" state
        if game.state == "DISCONNECTED":
            # Check if the game has been disconnected for over 1 minute
            if now() - game.updated_at > timedelta(minutes=1):
                # Mark the game as finished
                game.state = "ABORTED"
                game.finished = True
                game.updated_at = now()
                game.save()
                print(f"Game {game.id} has been marked as finished due to prolonged disconnection.")

    except Game.DoesNotExist:
        print(f"Game {game_id} does not exist.")
    except Exception as e:
        print(f"Error in monitoring game {game_id}: {str(e)}")


class GameServiceHandler(game_pb2_grpc.GameServiceServicer):
    def __init__(self):
        self.game_ready_subscribers = {}
        pass

    def GetGame(self, request, context):
        logger.info(f"GetGame Fetching game with ID {request.game_id}")
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
        logger.info(f"GetOnGoingGameByUser Fetching game for player ID {request.user_id}")
        try:
            # Fetch the game from the database
            game = (
                    Game.objects.filter(player_a_id=request.user_id, finished=False)
                    .exclude(state='FRIEND')
                    .first() or
                    Game.objects.filter(player_b_id=request.user_id, finished=False)
                    .exclude(state='FRIEND')
                    .first()
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
        logger.info(f"CreateGame Request received for player ID {request.player_id}")
        try:
            # Check if there's an existing game for the user
            existing_game = (
                Game.objects.filter(
                    finished=False,
                    player_a_id=request.player_id
                ).exclude(state='FRIEND').first() or
                Game.objects.filter(
                    finished=False,
                    player_b_id=request.player_id
                ).exclude(state='FRIEND').first()
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
            #  errors and return gRPC error response
            context.set_details(f"Error creating or finding game: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return game_pb2.Game()

    def GetOngoingGames(self, request, context):
        logger.info("GetOngoingGames Fetching all ongoing games")
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
        logger.info(f"StartGame Request received for game ID {request.game_id}")
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
        GRPC_STAT_HOST = "stat_service"
        GRPC_STAT_PORT = "50051"
        GRPC_STAT_TARGET = f"{GRPC_STAT_HOST}:{GRPC_STAT_PORT}"
        stat_channel = grpc.insecure_channel(GRPC_STAT_TARGET)
        stat_stub = StatServiceStub(stat_channel)

        GRPC_CHAT_HOST = "chat_service"
        GRPC_CHAT_PORT = "50051"
        GRPC_CHAT_TARGET = f"{GRPC_CHAT_HOST}:{GRPC_CHAT_PORT}"
        chat_channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
        chat_stub = chat_pb2_grpc.ChatRoomControllerStub(chat_channel)
        logger.info(f"HandleGameFinished Request received for game ID {request.game_id}")
        try:
            # Fetch the game from the database
            game = Game.objects.get(id=request.game_id)
            is_tournament_game = TournamentGameMapping.objects.filter(game_id=game.id).exists()


            # Update game stats
            game.points_player_a = request.points_player_a
            game.points_player_b = request.points_player_b
            game.state = "finished"
            game.finished = True

            # Determine the winner and save it as part of the game's state
            if request.winner_player_id == game.player_a_id:
                winner_id = game.player_a_id
                loser_id = game.player_b_id
            elif request.winner_player_id == game.player_b_id:
                winner_id = game.player_b_id
                loser_id = game.player_a_id
            else:
                game.save()
                return Empty()
            if is_tournament_game:
                try:
                    tournament_mapping = TournamentGameMapping.objects.get(game_id=game.id)
                    tournament_room = tournament_mapping.tournament_room
                    winner_tournament_user = TournamentUser.objects.filter(
                        tournament_room=tournament_room,
                        user_id=winner_id
                    ).first()

                    if winner_tournament_user:
                        logger.info(f"Winner User {winner_id} is part of TournamentRoom {tournament_room.id}")
                        winner_tournament_user.games_played += 1
                        winner_tournament_user.state= "WAITING"
                        winner_tournament_user.save()

                    else:
                        logger.warning(
                            f"Winner {winner_id} is not a participant in TournamentRoom {tournament_room.id}")
                except TournamentGameMapping.DoesNotExist:
                    logger.error(f"Tournament mapping not found for Game {game.id}")
                except Exception as e:
                    logger.error(f"Error while determining tournament winner: {str(e)}")

            game.save()
            create_stat_request = CreateStatRequest(
                game_id=request.game_id,
                winner_id=winner_id,
                loser_id=loser_id
            )
            create_stat_response = stat_stub.CreateStat(create_stat_request)

            # List all chat rooms and find the one associated with the game
            logger.info(f"Listing chat rooms to find the one associated with game {request.game_id}")
            chat_rooms = chat_stub.List(chat_pb2.ChatRoomListRequest())
            for chat_room in chat_rooms.results:
                logger.debug(f"Checking chat room {chat_room.id} associated with game {chat_room.game_id}")
                if chat_room.game_id == request.game_id:
                    chat_stub.Destroy(chat_pb2.ChatRoomDestroyRequest(id=chat_room.id))
                    logger.info(f"Destroyed chat room {chat_room.id} associated with game {request.game_id}")
                    break

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
                logger.debug("Fetching the latest state for the game with ID: %s", game.id)
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
                logger.debug("Stopping stream after game state READY for game ID: %s", game.id)
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

    def CreateFriendGame(self, request, context):
        """
            Creates a game between two specific players (player_a and player_b).
            The game is directly set to state "READY".
            Input: CreateFriendGameRequest contains both players' IDs.
            """
        try:
            # Validate that both players are provided
            if not request.player_a or not request.player_b:
                context.set_details("Both player_a and player_b must be provided.")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return game_pb2.Game()

            # Check if either player is already in an unfinished game
            existing_game_a = Game.objects.filter(
                finished=False,
                player_a_id=request.player_a
            ).first() or Game.objects.filter(
                finished=False,
                player_b_id=request.player_a
            ).first()

            existing_game_b = Game.objects.filter(
                finished=False,
                player_a_id=request.player_b
            ).first() or Game.objects.filter(
                finished=False,
                player_b_id=request.player_b
            ).first()
            existing_exact_game = Game.objects.filter(
                finished=False,
                player_a_id=request.player_a,
                player_b_id=request.player_b
            ).first() or Game.objects.filter(
                finished=False,
                player_a_id=request.player_b,
                player_b_id=request.player_a
            ).first()

            if existing_game_a or existing_game_b:
                if existing_exact_game:
                    response = game_pb2.Game(
                        id=existing_exact_game.id,
                        state=existing_exact_game.state,
                        points_player_a=existing_exact_game.points_player_a,
                        points_player_b=existing_exact_game.points_player_b,
                        player_a_id=existing_exact_game.player_a_id,
                        player_b_id=existing_exact_game.player_b_id,
                        finished=existing_exact_game.finished,
                    )
                    return response
                context.set_details("One of the players is already in an active game.")
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                return game_pb2.Game()

            # Create the new game in the "READY" state
            new_game = Game(
                player_a_id=request.player_a,
                player_b_id=request.player_b,
                points_player_a=0,
                points_player_b=0,
                state="FRIEND",
                finished=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            new_game.save()

            # Prepare the gRPC response
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
            # Handle unexpected errors
            context.set_details(f"Error creating friend game: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return game_pb2.Game()


    def UpdateGameState(self, request, context):
        """
            Updates the state of a game.
            Input: UpdateGameStateRequest contains the game ID and the new state.
            """
        try:
            # Fetch game by ID
            game = Game.objects.get(id=request.id)
            updated_state = request.state.upper()

            # Update the game state
            game.state = updated_state
            if updated_state == "FINISHED":
                game.finished = True
            game.updated_at = datetime.now()  # Update the timestamp
            game.save()
            if updated_state == "DISCONNECTED":
                monitor_thread = threading.Thread(target=monitor_disconnected_game, args=(game.id,))
                monitor_thread.start()
            # Prepare the gRPC response
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
            # Handle case where the game does not exist
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Game with ID {request.id} not found.")
            return game_pb2.Game()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error updating game state: {str(e)}")
            return game_pb2.Game()

    @classmethod
    def as_servicer(cls):
        return cls()
