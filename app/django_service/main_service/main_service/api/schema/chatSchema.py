import asyncio
from asyncio.log import logger
from datetime import datetime
from queue import Empty
import channels_graphql_ws
import grpc
import graphene
from main_service.protos import chat_pb2, chat_pb2_grpc


# Set up the gRPC target for Chat Service
GRPC_CHAT_HOST = "chat_service"
GRPC_CHAT_PORT = "50051"
GRPC_CHAT_TARGET = f"{GRPC_CHAT_HOST}:{GRPC_CHAT_PORT}"

class ChatRoomMessageType(graphene.ObjectType):
    id = graphene.Int()
    content = graphene.String()
    sender_id = graphene.Int()
    chat_room_id = graphene.Int()
    timestamp = graphene.String()

class ChatRoomUserType(graphene.ObjectType):
    id = graphene.Int()
    user_id = graphene.Int()
    chat_room_id = graphene.Int()
    joined_at = graphene.DateTime()

class ChatRoomType(graphene.ObjectType):
    id = graphene.Int()
    game_id = graphene.Int()
    name = graphene.String()
    created_at = graphene.DateTime()
    users = graphene.List(ChatRoomUserType)
    messages = graphene.List(ChatRoomMessageType)

class Query(graphene.ObjectType):
    chat_rooms_for_user = graphene.List(ChatRoomType, user_id=graphene.Int(required=True))

    async def resolve_chat_rooms_for_user(self, info, user_id):
        """
        Resolve the chat rooms for a specific user by their user_id.

        Args:
            info: The GraphQL context.
            user_id: The ID of the user for whom to fetch chat rooms.

        Returns:
            A list of ChatRoomType instances associated with the specified user.
        """
        try:
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            stub = chat_pb2_grpc.ChatRoomUserControllerStub(channel)

            grpc_request = chat_pb2.ChatRoomUserGetChatRoomByUserIdRequest(user_id=user_id)
            chat_rooms_response = stub.GetChatRoomByUserId(grpc_request)

            chat_rooms = []
            async for chat_room in chat_rooms_response:
                chat_rooms.append(
                    ChatRoomType(
                        id=chat_room.id,
                        name=chat_room.name,
                        created_at=datetime.fromtimestamp(chat_room.created_at.seconds),
                        game_id=chat_room.game_id,
                    )
                )

            return chat_rooms

        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.details()} (Code: {e.code().name})")
            return []  # Return an empty list if an error occurs
        except Exception as ex:
            logger.error(f"Unexpected error: {str(ex)}")
            return []  # Return an empty list if an unexpected error occurs

import asyncio


class PingType(graphene.ObjectType):
    response = graphene.String()

class PingSubscription(channels_graphql_ws.Subscription):
    response = graphene.Field(PingType)

    @staticmethod
    def subscribe(self, info):
        del info
        asyncio.create_task(PingSubscription.send_ping(self))
    @classmethod
    async def publish(cls, payload, info):
        """
        Publish the payload to the subscribers.
        This method is called when the subscription is triggered.
        """
        return PingType(response=payload["response"])  # Return the response field.

    @classmethod
    async def send_ping(cls, subscription_instance):
        """
        Broadcast a message to all subscribers in the 'ping_group'.
        """
        while True:
            await cls.broadcast_async(
                group="ping_group",  # All subscribers of the group receive the message.
                payload={"response": "ping"},  # Message content.
            )
            await asyncio.sleep(1)  # Wait for 1 second before sending the next message.

class Subscription(graphene.ObjectType):
    ping_test = PingSubscription.Field()

class ChatRoomMessageSubscription(channels_graphql_ws.Subscription):
    """GraphQL subscription for chat room messages."""
    message = graphene.Field(ChatRoomMessageType)

    class Arguments:
        chat_room_id = graphene.Int(required=True)

    @staticmethod
    def subscribe(root, info, chat_room_id):
        # Subscribe to chat room messages
        asyncio.create_task(ChatRoomMessageSubscription.subscribe_chat_room_messages(chat_room_id))
        return [f"chat_room_{chat_room_id}"]

    @classmethod
    async def publish(cls, payload, info):
        """
        Publish the payload to the subscribers.

        Args:
            payload: The data to be sent to subscribers.
            info: The GraphQL context.
        """
        await cls.broadcast(
            group=f"chat_room_{payload['chat_room_id']}",
            payload={"message": payload}
        )

    @staticmethod
    async def subscribe_chat_room_messages(chat_room_id):
        async with grpc.aio.insecure_channel(GRPC_CHAT_TARGET) as channel:
            stub = chat_pb2_grpc.ChatRoomMessageControllerStub(channel)
            async for response_message in stub.SubscribeChatRoomMessages(chat_pb2.ChatRoomMessageSubscribeChatRoomMessagesRequest(chat_room_id=chat_room_id)):
                payload = {
                    "id": response_message.id,
                    "content": response_message.content,
                    "sender_id": response_message.sender_id,
                    "chat_room_id": response_message.chat_room_id,
                    "timestamp": response_message.timestamp.ToDatetime().isoformat(),
                }
                await ChatRoomMessageSubscription.new_chat_message(chat_room_id, payload)

    @classmethod
    async def new_chat_message(cls, chat_room_id, payload):
        # Broadcast the new message to the subscription
        await cls.broadcast(
            group=f"chat_room_{chat_room_id}",
            payload=payload
        )

    #async def subscribe_chat_room_messages(chat_room_id):
    #    logger.debug(f"Subscribing to chat room messages for chat room ID: {chat_room_id}")
    #    async with grpc.aio.insecure_channel(GRPC_CHAT_TARGET) as channel:
    #        stub = chat_pb2_grpc.ChatRoomMessageControllerStub(channel)
    #        async for response_message in stub.SubscribeChatRoomMessages(chat_pb2.ChatRoomMessageSubscribeChatRoomMessagesRequest(chat_room_id=chat_room_id)):
    #            # Check if timestamp is a protobuf Timestamp or a string
    #            if isinstance(response_message.timestamp, str):
    #                # If it's a string, parse it accordingly
    #                timestamp = datetime.fromisoformat(response_message.timestamp)
    #            else:
    #                # If it's a protobuf Timestamp, convert it
    #                timestamp = response_message.timestamp.ToDatetime()

    #            payload = {
    #                "id": response_message.id,
    #                "content": response_message.content,
    #                "sender_id": response_message.sender_id,
    #                "chat_room_id": response_message.chat_room_id,
    #                "timestamp": timestamp.isoformat(),
    #            }
    #            await ChatRoomMessageSubscription.new_chat_message(chat_room_id, payload)

class Mutation(graphene.ObjectType):
    Empty

#class Subscription(graphene.ObjectType):
#	chat_room_message = ChatRoomMessageSubscription.Field()

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription) # mutation=Mutation, subscription=Subscription)
