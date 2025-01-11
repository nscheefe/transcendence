import logging
import asyncio
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
import graphene
import channels_graphql_ws

from main_service.protos.chat_pb2_grpc import ChatRoomUserControllerStub, ChatRoomMessageControllerStub, ChatRoomControllerStub
from main_service.protos.chat_pb2 import ChatRoomUserGetChatRoomByUserIdRequest, ChatRoomMessageListRequest, ChatRoomUserListRequest, ChatRoomUserRequest, ChatRoomMessageRequest, ChatRoomRequest, ChatRoomMessageSubscribeChatRoomMessagesRequest

# Set up the gRPC target for Chat Service
GRPC_CHAT_HOST = "chat_service"
GRPC_CHAT_PORT = "50051"
GRPC_CHAT_TARGET = f"{GRPC_CHAT_HOST}:{GRPC_CHAT_PORT}"

# Define GraphQL types
class ChatRoomMessageType(graphene.ObjectType):
    id = graphene.Int()
    content = graphene.String()
    sender_id = graphene.Int()
    chat_room_id = graphene.Int()
    timestamp = graphene.DateTime()

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

    def resolve_users(self, info):
        """Fetch users from a chat room using gRPC."""
        try:
            # Establish gRPC channel for user service
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            client = ChatRoomUserControllerStub(channel)

            # Prepare and send the request
            request = ChatRoomUserListRequest(chat_room_id=self.id)
            response = client.GetUsersByChatRoomId(request)
            logger.debug(f"Chat room users response: {response}")
            # Process and return the response
            return [
                ChatRoomUserType(
                    id=user.id,
                    user_id=user.user_id,
                    chat_room_id=user.chat_room_id,
                    joined_at=datetime.fromtimestamp(user.joined_at.seconds)
                )
                for user in response.results
            ]
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return []  # Return empty list if no users found
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
        except Exception as ex:
            raise Exception(f"Unexpected error: {str(ex)}")

    def resolve_messages(self, info):
        """Fetch messages from a chat room using gRPC."""
        try:
            # Establish gRPC channel for message service
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            client = ChatRoomMessageControllerStub(channel)

            # Prepare and send the request
            request = ChatRoomMessageListRequest(chat_room_id=self.id)
            response = client.GetMessagesByChatRoomId(request)
            logger.debug(f"Chat room messages response: {response}")
            return [
                ChatRoomMessageType(
                    id=msg.id,
                    content=msg.content,
                    sender_id=msg.sender_id,
                    chat_room_id=msg.chat_room_id,
                    timestamp=datetime.fromtimestamp(msg.timestamp.seconds)
                )
                for msg in response.results
            ]
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return []
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
        except Exception as ex:
            raise Exception(f"Unexpected error: {str(ex)}")

class Query(graphene.ObjectType):
    chat_room_users = graphene.List(ChatRoomUserType, id=graphene.Int(required=True))
    chat_rooms_for_user = graphene.List(ChatRoomType)

    @staticmethod
    def resolve_chat_room_users(root, info, id):
        """Resolve all users in a chat room by chat room ID via gRPC."""
        try:
            # Establish connection to gRPC service
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            user_client = ChatRoomUserControllerStub(channel)

            # Fetch users in the chat room
            user_request = ChatRoomUserListRequest(chat_room_id=id)
            user_response = user_client.GetUsersByChatRoomId(user_request)
            logger.debug(f"Chat room users response: {user_response}")
            users = [
                ChatRoomUserType(
                    id=user.id,
                    user_id=user.user_id,
                    chat_room_id=user.chat_room_id,
                    joined_at=datetime.fromtimestamp(user.joined_at.seconds)
                )
                for user in user_response.results
            ]
            return users

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return []  # Return empty list if no users found
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
        except Exception as ex:
            raise Exception(f"Unexpected error: {str(ex)}")

    @staticmethod
    async def resolve_chat_rooms_for_user(root, info):
        """
        Fetch multiple chat rooms for a user using resolve_chat_room.
        """
        try:
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            stub = ChatRoomUserControllerStub(channel)

            grpc_request = ChatRoomUserGetChatRoomByUserIdRequest(user_id=info.context.user_id)
            chat_rooms_response = stub.GetChatRoomByUserId(grpc_request)
            logger.debug(f"Chat rooms response: {chat_rooms_response.response}")
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
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return []  # If no chat rooms found, return empty list
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
        except Exception as ex:
            raise Exception(f"Unexpected error: {str(ex)}")

########################################################################################################################

# Mutation for managing chat operations
class AddUserToChatInput(graphene.InputObjectType):
    chat_room_id = graphene.Int(required=True)
    user_id = graphene.Int(required=True)

class AddUserToChatRoomMutation(graphene.Mutation):
    class Arguments:
        input = AddUserToChatInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:
            # Connect to gRPC ChatRoomUserService
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            stub = ChatRoomUserControllerStub(channel)

            request = ChatRoomUserRequest(
                chat_room_id=input["chat_room_id"],
                user_id=input["user_id"]
            )

            stub.AddUserToChatRoom(request)

            return AddUserToChatRoomMutation(
                success=True,
                message="User successfully added to the chat room."
            )
        except grpc.RpcError as e:
            return AddUserToChatRoomMutation(
                success=False,
                message=f"gRPC error: {e.details()} (Code: {str(e.code())})"
            )
        except Exception as ex:
            return AddUserToChatRoomMutation(
                success=False,
                message=f"Unexpected error: {str(ex)}"
            )

class CreateMessageInput(graphene.InputObjectType):
    chat_room_id = graphene.Int(required=True)
    content = graphene.String(required=True)

class CreateChatRoomInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    game_id = graphene.Int()

class CreateChatRoomMessageMutation(graphene.Mutation):
    class Arguments:
        input = CreateMessageInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:
            # Connect to gRPC ChatRoomMessageService
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            stub = ChatRoomMessageControllerStub(channel)

            # Prepare the gRPC CreateChatRoomMessage request
            request = ChatRoomMessageRequest(
                chat_room=input.chat_room_id,  # Use the correct field name
                content=input.content,
                sender_id=info.context.user_id
            )

            stub.Create(request)

            return CreateChatRoomMessageMutation(
                success=True,
                message="Message created successfully in the chat room."
            )
        except grpc.RpcError as e:
            return CreateChatRoomMessageMutation(
                success=False,
                message=f"gRPC error: {e.details()} (Code: {e.code().name})"
            )
        except Exception as ex:
            return CreateChatRoomMessageMutation(
                success=False,
                message=f"Unexpected error: {str(ex)}"
            )

# Root Query and Mutation

class CreateChatRoomMutation(graphene.Mutation):
    class Arguments:
        input = CreateChatRoomInput(required=True)

    success = graphene.Boolean()
    chat_room = graphene.Field(lambda: ChatRoomType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:
            # Connect to gRPC ChatService
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            stub = ChatRoomControllerStub(channel)

            request = ChatRoomRequest(
                name=input["name"],
                game_id=input.get("game_id")
            )

            response = stub.Create(request)

            created_chat_room = ChatRoomType(
                id=response.id,
                name=response.name,
                created_at=response.created_at.ToDatetime(),
                game_id=response.game_id
            )
            chatRoomUserstub = ChatRoomUserControllerStub(channel)
            request = ChatRoomUserRequest(
                chat_room_id=created_chat_room.id,
                user_id=info.context.user_id,
            )
            chatRoomUserstub.AddUserToChatRoom(request)

            return CreateChatRoomMutation(
                success=True,
                chat_room=created_chat_room,
                message="Chat room created successfully."
            )
        except grpc.RpcError as e:
            return CreateChatRoomMutation(
                success=False,
                chat_room=None,
                message=f"gRPC error: {e.details()} (Code: {str(e.code())})"
            )
        except Exception as ex:
            return CreateChatRoomMutation(
                success=False,
                chat_room=None,
                message=f"Unexpected error: {str(ex)}"
            )

class Mutation(graphene.ObjectType):
    manage_chat = CreateChatRoomMutation.Field()
    add_user_to_chat_room = AddUserToChatRoomMutation.Field()
    create_chat_room_message = CreateChatRoomMessageMutation.Field()
    create_chat_room = CreateChatRoomMutation.Field()

# GraphQL Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

logger = logging.getLogger('grpc')

async def subscribe_chat_room_messages(cls, chat_room_id):
    logger.debug(f"Subscribing to chat room messages for chat room ID: {chat_room_id}")
    try:
        async with grpc.aio.insecure_channel(GRPC_CHAT_TARGET) as channel:
            stub = ChatRoomMessageControllerStub(channel)
            request = ChatRoomMessageSubscribeChatRoomMessagesRequest(chat_room_id=chat_room_id)
            async for response in stub.SubscribeChatRoomMessages(request):
                timestamp = Timestamp()
                timestamp.FromDatetime(response.timestamp.ToDatetime())
                logger.debug(f"Received message: {response.content}")
                await cls.new_chat_message(
                    chat_room_id=chat_room_id,
                    payload={
                        "id": response.id,
                        "content": response.content,
                        "sender_id": response.sender_id,
                        "chat_room_id": response.chat_room_id,
                        "timestamp": timestamp.ToJsonString(),
                    }
                )
    except grpc.RpcError as e:
        logger.error(f"Error subscribing to chat room messages: {e}")
        raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
    except Exception as ex:
        logger.error(f"Unexpected error: {str(ex)}")
        raise Exception(f"Unexpected error: {str(ex)}")

class ChatRoomMessageSubscription(channels_graphql_ws.Subscription):
    """GraphQL subscription for chat room messages."""
    message = graphene.Field(ChatRoomMessageType)

    class Arguments:
        chat_room_id = graphene.Int(required=True)

    @staticmethod
    def subscribe(root, info, chat_room_id):
        logger.debug(f"Subscribing to chat room messages for chat room ID: {chat_room_id}")
        return [f"chat_room_{chat_room_id}"]

    @staticmethod
    def publish(payload, info, chat_room_id):
        logger.debug(f"Publishing message for chat room ID: {chat_room_id}")
        return ChatRoomMessageSubscription(message=payload)

    @staticmethod
    async def send_message_update(chat_room_id, message):
        logger.debug(f"Sending message update for chat room ID: {chat_room_id}")
        await ChatRoomMessageSubscription.broadcast(
            group=f"chat_room_{chat_room_id}",
            payload=message,
        )

    @classmethod
    def new_chat_message(cls, chat_room_id, payload):
        logger.debug(f"New chat message for chat room ID: {chat_room_id}")
        cls.broadcast(
            group=f"chat_room_{chat_room_id}",
            payload=payload
        )

# Add the subscription to the schema
class Subscription(graphene.ObjectType):
    chat_room_message = ChatRoomMessageSubscription.Field()

schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
