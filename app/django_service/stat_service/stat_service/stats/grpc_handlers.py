import grpc
from stat_service.protos import stat_pb2_grpc, stat_pb2
from stat_service.stats.models import Stat, UserStat
from google.protobuf.timestamp_pb2 import Timestamp

class StatServiceHandler(stat_pb2_grpc.StatServiceServicer):
    def __init__(self):
        pass

    def GetStat(self, request, context):
        try:
            stat = Stat.objects.get(id=request.id)
            return stat_pb2.GetStatResponse(
                stat=stat_pb2.Stat(
                    id=stat.id,
                    game_id=stat.game_id,
                    winner_id=stat.winner_id,
                    loser_id=stat.loser_id,
                    created_at=stat.created_at
                )
            )
        except Stat.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Stat not found')
            return stat_pb2.GetStatResponse()

    def CreateStat(self, request, context):
        try:
            stat = Stat.objects.create(
                game_id=request.game_id,
                winner_id=request.winner_id,
                loser_id=request.loser_id
            )
            UserStat.objects.create(
                user_id=request.winner_id,
                stat_id=stat.id,
                did_win=True
            )
            UserStat.objects.create(
                user_id=request.loser_id,
                stat_id=stat.id,
                did_win=False
            )
            created_at_timestamp = Timestamp()
            created_at_timestamp.FromDatetime(stat.created_at)
            return stat_pb2.CreateStatResponse(
                stat=stat_pb2.Stat(
                    id=stat.id,
                    game_id=stat.game_id,
                    winner_id=stat.winner_id,
                    loser_id=stat.loser_id,
                    created_at=created_at_timestamp
                )
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating stat: {str(e)}")
            return stat_pb2.CreateStatResponse()

    def GetStatsByUserId(self, request, context):
        try:
            user_stats = UserStat.objects.filter(user_id=request.user_id)
            return stat_pb2.GetStatsByUserIdResponse(
                user_stats=[stat_pb2.UserStat(
                    id=user_stat.id,
                    user_id=user_stat.user_id,
                    stat_id=user_stat.stat_id,
                    did_win=user_stat.did_win
                ) for user_stat in user_stats]
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching stats for user: {str(e)}")
            return stat_pb2.GetStatsByUserIdResponse()

    def CalculateStats(self, request, context):
        try:
            total_games = UserStat.objects.filter(user_id=request.user_id).count()
            total_wins = UserStat.objects.filter(user_id=request.user_id, did_win=True).count()
            total_losses = total_games - total_wins

            return stat_pb2.CalculateStatsResponse(
                total_games=total_games,
                total_wins=total_wins,
                total_losses=total_losses
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error calculating stats for user: {str(e)}")
            return stat_pb2.CalculateStatsResponse()

    @classmethod
    def as_servicer(cls):
        return cls()


def grpc_handlers(server):
    stat_service_handler = StatServiceHandler.as_servicer()
    stat_pb2_grpc.add_StatServiceServicer_to_server(stat_service_handler, server)
