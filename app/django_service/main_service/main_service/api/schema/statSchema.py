from datetime import datetime

import grpc
from ariadne import ObjectType
from main_service.api.schema.objectTypes import query, mutation, subscription  # Shared objects
from main_service.protos.stat_pb2 import (
    GetStatRequest,
    CreateStatRequest,
    GetStatsByUserIdRequest,
    CalculateStatsRequest,
)
from main_service.protos.stat_pb2_grpc import StatServiceStub

# gRPC connection setup to stat service
GRPC_STAT_HOST = "stat_service"
GRPC_STAT_PORT = "50051"
GRPC_STAT_TARGET = f"{GRPC_STAT_HOST}:{GRPC_STAT_PORT}"
stat_channel = grpc.insecure_channel(GRPC_STAT_TARGET)
stat_stub = StatServiceStub(stat_channel)

# Create custom object for Stat type (if needed)

# --- Query Resolvers ---

@query.field("stat")
def resolve_stat(_, info, id):
    """
    Fetch a Stat by its ID from the StatService.
    """
    try:
        request = GetStatRequest(id=id)
        response = stat_stub.GetStat(request)
        return {
            "id": response.stat.id,
            "gameId": response.stat.game_id,
            "winnerId": response.stat.winner_id,
            "loserId": response.stat.loser_id,
            "createdAt": datetime.fromtimestamp(response.stat.created_at.seconds).isoformat()
            if response.stat.HasField("created_at")
            else None,
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return None
        else:
            raise e


@query.field("statsByUser")
def resolve_stats_by_user(_, info, userId):
    """
    Fetch UserStats by the User ID from the StatService,
    and include the full Stat details for each statId.
    """
    try:
        # Step 1: Fetch stats by userId (initial query for user stats)
        request = GetStatsByUserIdRequest(user_id=userId)
        response = stat_stub.GetStatsByUserId(request)

        # Step 2: Fetch full stat details for each statId
        enriched_stats = []  # List to store user stats with full stat details

        for user_stat in response.user_stats:
            try:
                # Fetch the full stat details for statId
                stat_request = GetStatRequest(id=user_stat.stat_id)
                stat_response = stat_stub.GetStat(stat_request)

                # Add the full stat details to the userStat
                enriched_stats.append({
                    "id": user_stat.id,
                    "userId": user_stat.user_id,
                    "didWin": user_stat.did_win,
                    "stat": {
                        "id": stat_response.stat.id,
                        "gameId": stat_response.stat.game_id,
                        "winnerId": stat_response.stat.winner_id,
                        "loserId": stat_response.stat.loser_id,
                        "createdAt": datetime.fromtimestamp(stat_response.stat.created_at.seconds).isoformat()
                        if stat_response.stat.HasField("created_at")
                        else None,
                    },
                })
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    # If the stat is not found, skip it (or handle it accordingly)
                    continue
                else:
                    raise e

        # Return the enriched stats with full stat details
        return enriched_stats

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return []  # Return an empty list if no stats are found
        else:
            raise e

@query.field("calculateUserStats")
def resolve_calculate_user_stats(_, info, userId):
    """
    Calculate aggregate statistics for a specific user.
    """
    try:
        request = CalculateStatsRequest(user_id=userId)
        response = stat_stub.CalculateStats(request)
        return {
            "totalGames": response.total_games,
            "totalWins": response.total_wins,
            "totalLosses": response.total_losses,
        }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")


# --- Mutation Resolvers ---

@mutation.field("createStat")
def resolve_create_stat(_, info, input):
    """
    Create a new Stat for a game with the provided details.
    """
    try:
        request = CreateStatRequest(
            game_id=input["gameId"],
            winner_id=input["winnerId"],
            loser_id=input["loserId"],
        )
        response = stat_stub.CreateStat(request)
        return {
            "success": True,
            "stat": {
                "id": response.stat.id,
                "gameId": response.stat.game_id,
                "winnerId": response.stat.winner_id,
                "loserId": response.stat.loser_id,
                "createdAt": datetime.fromtimestamp(response.stat.created_at.seconds).isoformat()
                if response.stat.HasField("created_at")
                else None,
            },
            "message": "Stat successfully created.",
        }
    except grpc.RpcError as e:
        return {
            "success": False,
            "stat": None,
            "message": f"Failed to create stat: {e.details()}",
        }


# --- Custom Object Resolvers (if needed) ---

# --- Integration with Other Schemas ---

# Combine all resolvers into the resolvers list, consistent with userSchema.py
resolvers = [query, mutation, subscription]
