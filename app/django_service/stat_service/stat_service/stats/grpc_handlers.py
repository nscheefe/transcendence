import grpc
from concurrent import futures
from stat_service.protos import stat_pb2_grpc, stat_pb2
from stat_service.stats.models import Stat

class StatServiceHandler(stat_pb2_grpc.StatServiceServicer):
    def __init__(self):
        pass

    def GetStat(self, request, context):
        try:
            stat = Stat.objects.get(id=request.id)
            return stat_pb2.Stat(
                id=stat.id
            )
        except Stat.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Stat not found')
            return stat_pb2.Stat()

    def CreateStat(self, request, context):
        stat = Stat(
            id=request.id
        )
        stat.save()
        return stat_pb2.Stat(
            id=stat.id
        )

    def GetStats(self, request, context):
        stats = Stat.objects.all()
        return stat_pb2.StatList(
            stats=[stat_pb2.Stat(id=stat.id) for stat in stats]
        )

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    stat_service_handler = StatServiceHandler.as_servicer()
    stat_pb2_grpc.add_StatServiceServicer_to_server(stat_service_handler, server)