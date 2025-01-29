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
                "chat_room_id": message.chat_room,
                "sender_id": message.sender_id,
                "content": message.content,
                "timestamp": datetime.fromtimestamp(message.timestamp.seconds).isoformat() if hasattr(message.timestamp, 'seconds') else message.timestamp,
            }

@subscription.field("chat_room_message")
def chat_room_message_resolver(message, info, chat_room_id):
    return message

@mutation.field("startChatWithUser")
def resolve_start_chat_with_user(_, info, user_id, game_id=None):
    current_user_id = info.context["request"].user_id
    if not current_user_id:
        raise Exception("Authentication required: user_id is missing")
    try:
        with grpc.insecure_channel(GRPC_CHAT_TARGET) as channel:
            # Create the chat room
            stub = chat_pb2_grpc.ChatRoomControllerStub(channel)
            grpc_request = chat_pb2.ChatRoomRequest(name=f"User-to-User {current_user_id}and{user_id}", game_id=game_id)
            response = stub.Create(grpc_request)

            # Add the current user to the chat room
            stub = chat_pb2_grpc.ChatRoomUserControllerStub(channel)
            grpc_request = chat_pb2.ChatRoomUserRequest(chat_room=response.id, user_id=current_user_id)
            current_user_response = stub.Create(grpc_request)

            # Add the other user to the chat room
            grpc_request = chat_pb2.ChatRoomUserRequest(chat_room=response.id, user_id=user_id)
            other_user_response = stub.Create(grpc_request)

            participants = [
                {
                    "user_id": current_user_response.user_id,
                    "chat_room_id": current_user_response.chat_room,
                    "id": current_user_response.id,
                    "joined_at": datetime.fromtimestamp(current_user_response.joined_at.seconds).isoformat() if hasattr(current_user_response.joined_at, 'seconds') else current_user_response.joined_at,
                },
                {
                    "user_id": other_user_response.user_id,
                    "chat_room_id": other_user_response.chat_room,
                    "id": other_user_response.id,
                    "joined_at": datetime.fromtimestamp(other_user_response.joined_at.seconds).isoformat() if hasattr(other_user_response.joined_at, 'seconds') else other_user_response.joined_at,
                }
            ]

            logger.info(f"Rpc response: {response}")
            logger.info(f"Chat room {response.id} created and users {current_user_id} and {user_id} added")

            return {
                "id": response.id,
                "name": response.name,
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat() if hasattr(response.created_at, 'seconds') else response.created_at,
                "game_id": response.game_id,
                "users": participants
            }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            logger.error(f"Room with this Name already exists: {e}")
            return None
        else:
            logger.error(f"An error occurred: {e}")
            raise e

@mutation.field("create_chat_room")
def resolve_create_chat_room(_, info, name, game_id=None):
    user_id = info.context["request"].user_id
    if not user_id:
        raise Exception("Authentication required: user_id is missing")
    try:
        with grpc.insecure_channel(GRPC_CHAT_TARGET) as channel:
            stub = chat_pb2_grpc.ChatRoomControllerStub(channel)
            grpc_request = chat_pb2.ChatRoomRequest(name=name, game_id=game_id)
            response = stub.Create(grpc_request)
            stub = chat_pb2_grpc.ChatRoomUserControllerStub(channel)
            grpc_request = chat_pb2.ChatRoomUserRequest(chat_room=response.id, user_id=user_id)
            user_response = stub.Create(grpc_request)
            participants = [{
                "user_id": user_response.user_id,
                "chat_room_id": user_response.chat_room,
                "id": user_response.id,
                "joined_at": datetime.fromtimestamp(user_response.joined_at.seconds).isoformat() if hasattr(user_response.joined_at, 'seconds') else user_response.joined_at,
            }]
            logger.info(f"Rpc response: {response}")
            logger.info(f"Chat room {response.id} created")
            return {
                "id": response.id,
                "name": response.name,
                "created_at": datetime.fromtimestamp(response.created_at.seconds).isoformat() if hasattr(response.created_at, 'seconds') else response.created_at,
                "game_id": response.game_id,
                "users": participants
            }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            logger.error(f"Room with this Name already exists: {e}")
            return None
        else:
            logger.error(f"An error occurred: {e}")
            raise e

@mutation.field("add_user_to_chat_room")
def resolve_add_user_to_chat_room(_, info, chat_room_id, user_id):
    with grpc.insecure_channel(GRPC_CHAT_TARGET) as channel:
        stub = chat_pb2_grpc.ChatRoomUserControllerStub(channel)
        grpc_request = chat_pb2.ChatRoomUserRequest(chat_room=chat_room_id, user_id=user_id)
        response = stub.Create(grpc_request)
        return {
            "id": response.id,
            "user_id": response.user_id,
            "chat_room_id": response.chat_room,
            "joined_at": datetime.fromtimestamp(response.joined_at.seconds).isoformat() if hasattr(response.joined_at, 'seconds') else response.joined_at,
        }

@mutation.field("create_chat_room_message")
def resolve_create_chat_room_message(_, info, chat_room_id, content):
    sender_id = info.context["request"].user_id
    with grpc.insecure_channel(GRPC_CHAT_TARGET) as channel:
        stub = chat_pb2_grpc.ChatRoomMessageControllerStub(channel)
        grpc_request = chat_pb2.ChatRoomMessageRequest(chat_room=chat_room_id, content=content, sender_id=sender_id)
        response = stub.Create(grpc_request)
        return {
            "id": response.id,
            "content": response.content,
            "sender_id": response.sender_id,
            "timestamp": datetime.fromtimestamp(response.timestamp.seconds).isoformat() if hasattr(response.timestamp, 'seconds') else response.timestamp,
            "chat_room_id": response.chat_room
        }

# Add the mutation to the resolver list
resolver = [query, mutation, subscription]

