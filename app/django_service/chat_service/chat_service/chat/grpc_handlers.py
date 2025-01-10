# Import gRPC protobuf definitions
from protos import chat_pb2_grpc, chat_pb2

# Import handler classes
from chat_service.chat.chat_grpc_handler import ChatServiceHandler, ChatStreamService, ChatService
from chat_service.chat.chat_room_message_grpc_handler import ChatRoomMessageServiceHandler
from chat_service.chat.chat_room_user_grpc_handler import ChatRoomUserServiceHandler


def grpc_handlers(server):
    # Register Chat Service
    chat_stream_service = ChatStreamService.as_servicer()
    # Stream Chat Room Messages
    chat_service_handler = ChatServiceHandler.as_servicer()
    chat_service = ChatService.as_servicer()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(chat_service_handler, chat_stream_service, chat_service, server)

    # Register Chat Room Message Service
    chat_room_message_service_handler = ChatRoomMessageServiceHandler.as_servicer()
    chat_pb2_grpc.add_ChatRoomMessageServiceServicer_to_server(chat_room_message_service_handler, server)

    # Register Chat Room User Service
    chat_room_user_service_handler = ChatRoomUserServiceHandler.as_servicer()
    chat_pb2_grpc.add_ChatRoomUserServiceServicer_to_server(chat_room_user_service_handler, server)


