from django_socio_grpc.services.app_handler_registry import AppHandlerRegistry
from .services import ChatRoomService, ChatRoomMessageService, ChatRoomUserService

def grpc_handlers(server):
    app_registry = AppHandlerRegistry("chat", server)
    app_registry.register(ChatRoomService)
    app_registry.register(ChatRoomMessageService)
    app_registry.register(ChatRoomUserService)
