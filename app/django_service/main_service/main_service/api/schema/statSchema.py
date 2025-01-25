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
from .userSchema import resolve_get_all_profiles
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

@query.field("StatList")
def get_profiles_with_calculated_stats(_, info):
    """
    Resolve all profiles, calculate stats for each profile, and sort them by highest win ratio.
    """
    try:
        print("[DEBUG] Starting StatList query resolver")
        print("[DEBUG] Fetching all profiles...")

        # Fetch profiles and handle the data structure
        raw_profiles = resolve_get_all_profiles(_, info, 10, 0)  # Adjust limit/offset as required
        profiles = raw_profiles.get('profiles', [])  # Extract the 'profiles' key, default to an empty list if missing
        total_count = raw_profiles.get('totalCount', 0)  # Extract 'totalCount' for debugging (if needed)
        print(f"[DEBUG] Profiles fetched: {profiles} (Total Count: {total_count})")

        # Validate profiles type
        if not isinstance(profiles, list):
            raise ValueError(f"Expected profiles to be a list, but got {type(profiles)}")

        profile_stats = []

        # Check if profiles list is empty
        if not profiles:
            print("[DEBUG] No profiles available to process. Returning an empty list.")
            return profile_stats  # Return an empty list if no profiles are available

        # Process each profile
        for profile in profiles:
        # Validate each profile entry
            if not isinstance(profile, dict):
                print(f"[ERROR] Invalid profile type: {type(profile)}. Skipping...")
                continue

            user_id = profile.get('userId')  # Safe key access with `.get()`
            if user_id is None:
                print(f"[ERROR] Profile missing 'id': {profile}. Skipping...")
                continue

            print(f"[DEBUG] Processing stats for profile with user_id: {user_id}")

            try:
                # gRPC request to get calculated stats for the user
                print(f"[DEBUG] Sending gRPC request for user_id: {user_id}")
                request = CalculateStatsRequest(user_id=user_id)
                response = stat_stub.CalculateStats(request)
                print(f"[DEBUG] Received gRPC response for user_id: {user_id} -> {response}")

                # Check if response is valid
                if not response:
                    print(f"[ERROR] Empty gRPC response for user_id: {user_id}. Skipping...")
                    continue

                # Calculate stats safely
                total_games = response.total_games
                total_wins = response.total_wins
                win_ratio = total_wins / total_games if total_games > 0 else 0

                print(f"[DEBUG] Calculated stats for user_id {user_id} - "
                      f"Total Games: {total_games}, Total Wins: {total_wins}, Win Ratio: {win_ratio:.2f}")

                # Append profile with calculated stats
                profile_stats.append({
                    "profile": profile,
                    "stats": {
                        "totalGames": response.total_games,
                        "totalWins": response.total_wins,
                        "totalLosses": response.total_losses,
                        "winRatio": win_ratio,
                    }
                })

            # Catch gRPC-specific errors
            except grpc.RpcError as e:
                print(f"[ERROR] gRPC error for user_id {user_id}: {e.details()}")
                continue

            # Catch unexpected errors
            except Exception as e:
                print(f"[ERROR] Unexpected error for user_id {user_id}: {str(e)}")
                continue

        # Sort profiles by highest win ratio
        if profile_stats:
            print("[DEBUG] Sorting profiles by win ratio...")
            sorted_profiles = sorted(profile_stats, key=lambda x: x['stats']['winRatio'], reverse=True)
            print(f"[DEBUG] Sorting complete. Number of profiles sorted: {len(sorted_profiles)}")
            return sorted_profiles

        # Return an empty list if no valid stats were generated
        print("[DEBUG] No valid stats generated. Returning an empty list.")
        return profile_stats

    except Exception as e:
        print(f"[ERROR] Unexpected error in get_profiles_with_calculated_stats: {str(e)}")
        return []

# --- Integration with Other Schemas ---

# Combine all resolvers into the resolvers list, consistent with userSchema.py
resolvers = [query, mutation, subscription]
