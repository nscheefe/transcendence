import asyncio
from asyncio.log import logger
from datetime import datetime
import grpc
from ariadne import ObjectType
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
        stub = chat_pb2_grpc.ChatRoomControllerStub(channel)
        grpc_request = chat_pb2.ChatRoomGetChatRoomByUserIdRequest(user_id=user_id)
        async for chat_room in stub.GetChatRoomByUserId(grpc_request):
            logger.info(f"Chat room {chat_room.id} found for user {user_id}")
            participants = [
                {
                    "user_id": participant.user_id,
                    "chat_room_id": participant.chat_room,  # Ensure this matches the expected field name
                    "id": participant.id,
                    "joined_at": datetime.fromtimestamp(participant.joined_at.seconds).isoformat() if hasattr(participant.joined_at, 'seconds') else participant.joined_at,
                }
                for participant in chat_room.participants
            ]
            yield {
                "id": chat_room.id,
                "name": chat_room.name,
                "created_at": datetime.fromtimestamp(chat_room.created_at.seconds).isoformat() if hasattr(chat_room.created_at, 'seconds') else chat_room.created_at,
                "game_id": chat_room.game_id,
                "users": participants if participants else [],
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
        grpc_request = chat_pb2.ChatRoomMessageSubscribeChatRoomMessagesRequest(chat_room_id=chat_room_id)
        async for message in stub.SubscribeChatRoomMessages(grpc_request):
            yield {
                "id": message.id,
                "chat_room_id": message.chat_room_id,
                "user_id": message.user_id,
                "content": message.content,
                "created_at": datetime.fromtimestamp(message.created_at.seconds).isoformat() if hasattr(message.created_at, 'seconds') else message.created_at,
            }

@subscription.field("chat_room_message")
def chat_room_message_resolver(message, info, chat_room_id):
    return message

resolver = [query, mutation, subscription]

