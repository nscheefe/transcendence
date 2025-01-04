import graphene
import grpc

from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from main_service.protos.stat_pb2_grpc import StatServiceStub
from main_service.protos.stat_pb2 import (
    GetStatRequest,
    CreateStatRequest,
    GetStatsByUserIdRequest,
    CalculateStatsRequest
)

GRPC_STAT_HOST = "stat_service"
GRPC_STAT_PORT = "50051"
GRPC_STAT_TARGET = f"{GRPC_STAT_HOST}:{GRPC_STAT_PORT}"


class StatType(graphene.ObjectType):
    id = graphene.Int()
    game_id = graphene.Int()
    winner_id = graphene.Int()
    loser_id = graphene.Int()
    created_at = graphene.DateTime()


class UserStatType(graphene.ObjectType):
    id = graphene.Int()
    user_id = graphene.Int()
    stat_id = graphene.Int()
    did_win = graphene.Boolean()


class CalculateStatsResponseType(graphene.ObjectType):
    total_games = graphene.Int()
    total_wins = graphene.Int()
    total_losses = graphene.Int()


class Query(graphene.ObjectType):
    stat = graphene.Field(StatType, id=graphene.Int(required=True))
    stats_by_user = graphene.List(UserStatType, user_id=graphene.Int(required=True))
    calculate_user_stats = graphene.Field(
        CalculateStatsResponseType, user_id=graphene.Int(required=True)
    )

    def resolve_stat(self, info, id):
        try:
            channel = grpc.insecure_channel(GRPC_STAT_TARGET)
            client = StatServiceStub(channel)

            request = GetStatRequest(id=id)
            response = client.GetStat(request)

            if not response.stat.id:
                raise Exception(f"Stat with ID {id} not found.")

            return StatType(
                id=response.stat.id,
                game_id=response.stat.game_id,
                winner_id=response.stat.winner_id,
                loser_id=response.stat.loser_id,
                created_at=datetime.fromtimestamp(response.stat.created_at.seconds),
            )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
        except Exception as ex:
            raise Exception(f"Unexpected error: {str(ex)}")

    def resolve_stats_by_user(self, info, user_id):
        try:
            channel = grpc.insecure_channel(GRPC_STAT_TARGET)
            client = StatServiceStub(channel)

            request = GetStatsByUserIdRequest(user_id=user_id)
            response = client.GetStatsByUserId(request)

            return [
                UserStatType(
                    id=stat.id,
                    user_id=stat.user_id,
                    stat_id=stat.stat_id,
                    did_win=stat.did_win
                )
                for stat in response.user_stats
            ]
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
        except Exception as ex:
            raise Exception(f"Unexpected error: {str(ex)}")

    def resolve_calculate_user_stats(self, info, user_id):
        try:
            channel = grpc.insecure_channel(GRPC_STAT_TARGET)
            client = StatServiceStub(channel)

            request = CalculateStatsRequest(user_id=user_id)
            response = client.CalculateStats(request)

            return CalculateStatsResponseType(
                total_games=response.total_games,
                total_wins=response.total_wins,
                total_losses=response.total_losses
            )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
        except Exception as ex:
            raise Exception(f"Unexpected error: {str(ex)}")


class CreateStatInput(graphene.InputObjectType):
    game_id = graphene.Int(required=True)
    winner_id = graphene.Int(required=True)
    loser_id = graphene.Int(required=True)


class CreateStatMutation(graphene.Mutation):
    class Arguments:
        input = CreateStatInput(required=True)

    stat = graphene.Field(StatType)
    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:

            channel = grpc.insecure_channel(GRPC_STAT_TARGET)
            client = StatServiceStub(channel)

            request = CreateStatRequest(
                game_id=input.game_id,
                winner_id=input.winner_id,
                loser_id=input.loser_id,
            )
            response = client.CreateStat(request)

            return CreateStatMutation(
                success=True,
                stat=StatType(
                    id=response.stat.id,
                    game_id=response.stat.game_id,
                    winner_id=response.stat.winner_id,
                    loser_id=response.stat.loser_id,
                    created_at=datetime.fromtimestamp(response.stat.created_at.seconds)
                ),
                message="Stat created successfully."
            )
        except grpc.RpcError as e:
            return CreateStatMutation(
                success=False,
                stat=None,
                message=f"gRPC error: {e.details()} (Code: {e.code().name})",
            )
        except Exception as ex:
            return CreateStatMutation(
                success=False,
                stat=None,
                message=f"Unexpected error: {str(ex)}",
            )


class Mutation(graphene.ObjectType):
    create_stat = CreateStatMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
