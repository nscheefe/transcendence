import asyncio
from asyncio.log import logger
from datetime import datetime
import grpc
from ariadne import QueryType, MutationType, SubscriptionType, make_executable_schema, gql
from ariadne.asgi import GraphQL

from main_service.protos import chat_pb2, chat_pb2_grpc
from main_service.api.schema.objectTypes import query, mutation, subscription

# Set up the gRPC target for Chat Service
GRPC_CHAT_HOST = "chat_service"
GRPC_CHAT_PORT = "50051"
GRPC_CHAT_TARGET = f"{GRPC_CHAT_HOST}:{GRPC_CHAT_PORT}"

@subscription.source("chatRoomsForUser")
async def chat_rooms_for_user_source(_, info):
    user_id = info.context["request"].scope.get("user_id")
    if user_id is None:
        raise Exception("Authentication required")
    logger.info(f"User {user_id} is subscribing to chat rooms")
    async with grpc.aio.insecure_channel(GRPC_CHAT_TARGET) as channel:
        stub = chat_pb2_grpc.ChatRoomUserControllerStub(channel)
        grpc_request = chat_pb2.ChatRoomUserGetChatRoomByUserIdRequest(user_id=user_id)
        async for chat_room in stub.GetChatRoomByUserId(grpc_request):
            yield {
                "id": chat_room.id,
                "name": chat_room.name,
                "created_at": datetime.fromtimestamp(chat_room.created_at.seconds) if hasattr(chat_room.created_at, 'seconds') else chat_room.created_at,
                "game_id": chat_room.game_id,
            }

@subscription.field("chatRoomsForUser")
def chat_rooms_for_user_resolver(chat_room, info):
    return chat_room

@subscription.source("ping_test")
async def ping_test_source(_, info):
    while True:
        await asyncio.sleep(1)
        yield {"response": "ping"}

@subscription.field("ping_test")
def ping_test_resolver(message, info):
    return message

@subscription.source("chat_room_message")
async def chat_room_message_source(_, info, chat_room_id):
    async with grpc.aio.insecure_channel(GRPC_CHAT_TARGET) as channel:
        stub = chat_pb2_grpc.ChatRoomMessageControllerStub(channel)
        async for response_message in stub.SubscribeChatRoomMessages(chat_pb2.ChatRoomMessageSubscribeChatRoomMessagesRequest(chat_room_id=chat_room_id)):
            yield {
                "id": response_message.id,
                "content": response_message.content,
                "sender_id": response_message.sender_id,
                "chat_room_id": response_message.chat_room_id,
                "timestamp": response_message.timestamp.ToDatetime().isoformat(),
            }

@subscription.field("chat_room_message")
def chat_room_message_resolver(message, info):
    return message

resolver = [query, mutation, subscription]

