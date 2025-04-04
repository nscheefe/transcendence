# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from . import gameEvent_pb2 as gameEvent__pb2

GRPC_GENERATED_VERSION = '1.69.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in gameEvent_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class GameEventServiceStub(object):
    """Service definition for GameEvents
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetGameEvent = channel.unary_unary(
                '/transcendence.GameEventService/GetGameEvent',
                request_serializer=gameEvent__pb2.GetGameEventRequest.SerializeToString,
                response_deserializer=gameEvent__pb2.GameEvent.FromString,
                _registered_method=True)
        self.CreateGameEvent = channel.unary_unary(
                '/transcendence.GameEventService/CreateGameEvent',
                request_serializer=gameEvent__pb2.CreateGameEventRequest.SerializeToString,
                response_deserializer=gameEvent__pb2.GameEvent.FromString,
                _registered_method=True)


class GameEventServiceServicer(object):
    """Service definition for GameEvents
    """

    def GetGameEvent(self, request, context):
        """Get a specific game event by its ID
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateGameEvent(self, request, context):
        """Create a new game event
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GameEventServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetGameEvent': grpc.unary_unary_rpc_method_handler(
                    servicer.GetGameEvent,
                    request_deserializer=gameEvent__pb2.GetGameEventRequest.FromString,
                    response_serializer=gameEvent__pb2.GameEvent.SerializeToString,
            ),
            'CreateGameEvent': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateGameEvent,
                    request_deserializer=gameEvent__pb2.CreateGameEventRequest.FromString,
                    response_serializer=gameEvent__pb2.GameEvent.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'transcendence.GameEventService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('transcendence.GameEventService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class GameEventService(object):
    """Service definition for GameEvents
    """

    @staticmethod
    def GetGameEvent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/transcendence.GameEventService/GetGameEvent',
            gameEvent__pb2.GetGameEventRequest.SerializeToString,
            gameEvent__pb2.GameEvent.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CreateGameEvent(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/transcendence.GameEventService/CreateGameEvent',
            gameEvent__pb2.CreateGameEventRequest.SerializeToString,
            gameEvent__pb2.GameEvent.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
