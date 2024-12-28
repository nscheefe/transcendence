# Import gRPC protobuf definitions
from chat_service.protos import (
    chat_pb2_grpc,
    ChatRoomMessage_pb2_grpc,
    ChatRoomUser_pb2_grpc,
)

# Import handler classes
from chat_service.chat.chat_grpc_handler import ChatServiceHandler
from chat_service.chat.chat_room_message_grpc_handler import ChatRoomMessageServiceHandler
from chat_service.chat.chat_room_user_grpc_handler import ChatRoomUserServiceHandler


def grpc_handlers(server):
    # Register Chat Service
    chat_service_handler = ChatServiceHandler.as_servicer()
    ChatRoom_pb2_grpc.add_ChatServiceServicer_to_server(chat_service_handler, server)

    # Register Chat Room Message Service
    chat_room_message_service_handler = ChatRoomMessageServiceHandler.as_servicer()
    ChatRoomMessage_pb2_grpc.add_ChatRoomMessageServiceServicer_to_server(chat_room_message_service_handler, server)

    # Register Chat Room User Service
    chat_room_user_service_handler = ChatRoomUserServiceHandler.as_servicer()
    ChatRoomUser_pb2_grpc.add_ChatRoomUserServiceServicer_to_server(chat_room_user_service_handler, server)
