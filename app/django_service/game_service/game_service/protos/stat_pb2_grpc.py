# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import stat_pb2 as stat__pb2


class StatServiceStub(object):
    """The gRPC StatService definition
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateStat = channel.unary_unary(
                '/statservice.StatService/CreateStat',
                request_serializer=stat__pb2.CreateStatRequest.SerializeToString,
                response_deserializer=stat__pb2.CreateStatResponse.FromString,
                )
        self.GetStat = channel.unary_unary(
                '/statservice.StatService/GetStat',
                request_serializer=stat__pb2.GetStatRequest.SerializeToString,
                response_deserializer=stat__pb2.GetStatResponse.FromString,
                )
        self.GetStatsByUserId = channel.unary_unary(
                '/statservice.StatService/GetStatsByUserId',
                request_serializer=stat__pb2.GetStatsByUserIdRequest.SerializeToString,
                response_deserializer=stat__pb2.GetStatsByUserIdResponse.FromString,
                )
        self.CalculateStats = channel.unary_unary(
                '/statservice.StatService/CalculateStats',
                request_serializer=stat__pb2.CalculateStatsRequest.SerializeToString,
                response_deserializer=stat__pb2.CalculateStatsResponse.FromString,
                )


class StatServiceServicer(object):
    """The gRPC StatService definition
    """

    def CreateStat(self, request, context):
        """Create a new Stat
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStat(self, request, context):
        """Get a specific Stat by ID
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetStatsByUserId(self, request, context):
        """Get all UserStats by User ID
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CalculateStats(self, request, context):
        """Calculate aggregate statistics for a user
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_StatServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateStat': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateStat,
                    request_deserializer=stat__pb2.CreateStatRequest.FromString,
                    response_serializer=stat__pb2.CreateStatResponse.SerializeToString,
            ),
            'GetStat': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStat,
                    request_deserializer=stat__pb2.GetStatRequest.FromString,
                    response_serializer=stat__pb2.GetStatResponse.SerializeToString,
            ),
            'GetStatsByUserId': grpc.unary_unary_rpc_method_handler(
                    servicer.GetStatsByUserId,
                    request_deserializer=stat__pb2.GetStatsByUserIdRequest.FromString,
                    response_serializer=stat__pb2.GetStatsByUserIdResponse.SerializeToString,
            ),
            'CalculateStats': grpc.unary_unary_rpc_method_handler(
                    servicer.CalculateStats,
                    request_deserializer=stat__pb2.CalculateStatsRequest.FromString,
                    response_serializer=stat__pb2.CalculateStatsResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'statservice.StatService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class StatService(object):
    """The gRPC StatService definition
    """

    @staticmethod
    def CreateStat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/statservice.StatService/CreateStat',
            stat__pb2.CreateStatRequest.SerializeToString,
            stat__pb2.CreateStatResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetStat(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/statservice.StatService/GetStat',
            stat__pb2.GetStatRequest.SerializeToString,
            stat__pb2.GetStatResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetStatsByUserId(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/statservice.StatService/GetStatsByUserId',
            stat__pb2.GetStatsByUserIdRequest.SerializeToString,
            stat__pb2.GetStatsByUserIdResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CalculateStats(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/statservice.StatService/CalculateStats',
            stat__pb2.CalculateStatsRequest.SerializeToString,
            stat__pb2.CalculateStatsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
