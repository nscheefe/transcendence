import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
import graphene

from main_service.protos.ChatRoomMessage_pb2_grpc import ChatRoomMessageServiceStub
from main_service.protos.ChatRoomMessage_pb2 import GetMessagesByChatRoomIdRequest, CreateChatRoomMessageRequest
from main_service.protos.ChatRoomUser_pb2_grpc import ChatRoomUserServiceStub
from main_service.protos.ChatRoomUser_pb2 import GetUsersByChatRoomIdRequest, AddUserToChatRoomRequest

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
    name = graphene.String()
    created_at = graphene.DateTime()
    users = graphene.List(ChatRoomUserType)
    messages = graphene.List(ChatRoomMessageType)

    def resolve_users(self, info):
        """Fetch users from a chat room using gRPC."""
        try:
            # Establish gRPC channel for user service
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            client = ChatRoomUserServiceStub(channel)

            # Prepare and send the request
            request = GetUsersByChatRoomIdRequest(chat_room_id=self.id)
            response = client.GetUsersByChatRoomId(request)

            # Map response to GraphQL type
            return [
                ChatRoomUserType(
                    id=user.id,
                    user_id=user.user_id,
                    chat_room_id=user.chat_room_id,
                    joined_at=datetime.fromtimestamp(user.joined_at.seconds)
                )
                for user in response.users
            ]
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return []  # Return empty list if no users found
            raise Exception(f"gRPC error: {e.details()} (Code: {str(e.code())})")

    def resolve_messages(self, info):
        """Fetch messages from a chat room using gRPC."""
        try:
            # Establish gRPC channel for message service
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)
            client = ChatRoomMessageServiceStub(channel)

            # Prepare and send the request
            request = GetMessagesByChatRoomIdRequest(chat_room_id=self.id)
            response = client.GetMessagesByChatRoomId(request)

            # Map response to GraphQL type
            return [
                ChatRoomMessageType(
                    id=msg.id,
                    content=msg.content,
                    sender_id=msg.sender_id,
                    chat_room_id=msg.chat_room_id,
                    timestamp=datetime.fromtimestamp(msg.timestamp.seconds)
                )
                for msg in response.messages
            ]
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return []  # Return empty list if no messages found
            raise Exception(f"gRPC error: {e.details()} (Code: {str(e.code())})")


# Mutation for managing chat operations
class AddUserToChatInput(graphene.InputObjectType):
    chat_room_id = graphene.Int(required=True)
    user_id = graphene.Int(required=True)


class CreateMessageInput(graphene.InputObjectType):
    chat_room_id = graphene.Int(required=True)
    content = graphene.String(required=True)
    sender_id = graphene.Int(required=True)


class ManageChatMutation(graphene.Mutation):
    class Arguments:
        add_user_to_chat = AddUserToChatInput()
        create_message = CreateMessageInput()

    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, add_user_to_chat=None, create_message=None):
        """Perform chat management operations"""
        try:
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)

            # Add user to chat room
            if add_user_to_chat:
                user_stub = ChatRoomUserServiceStub(channel)
                add_request = AddUserToChatRoomRequest(
                    chat_room_id=add_user_to_chat.chat_room_id,
                    user_id=add_user_to_chat.user_id
                )
                user_stub.AddUserToChatRoom(add_request)

            # Create a message in the chat room
            if create_message:
                message_stub = ChatRoomMessageServiceStub(channel)
                create_request = CreateChatRoomMessageRequest(
                    chat_room_id=create_message.chat_room_id,
                    content=create_message.content,
                    sender_id=create_message.sender_id
                )
                message_stub.CreateMessage(create_request)

            return ManageChatMutation(success=True, message="Operation successful.")
        except grpc.RpcError as e:
            return ManageChatMutation(success=False, message=f"gRPC error: {e.details()} (Code: {str(e.code())})")
        except Exception as ex:
            return ManageChatMutation(success=False, message=f"Unexpected error: {str(ex)}")


# Root Query and Mutation
class Query(graphene.ObjectType):
    chat_room = graphene.Field(ChatRoomType, id=graphene.Int(required=True))

    @staticmethod
    def resolve_chat_room(root, info, id):
        """Resolve chat room by ID via gRPC."""
        try:
            # Establish connection to gRPC services
            channel = grpc.insecure_channel(GRPC_CHAT_TARGET)

            # Initialize stubs
            user_client = ChatRoomUserServiceStub(channel)
            message_client = ChatRoomMessageServiceStub(channel)

            # Fetch users from the chat room
            user_request = GetUsersByChatRoomIdRequest(chat_room_id=id)
            user_response = user_client.GetUsersByChatRoomId(user_request)

            users = [
                ChatRoomUserType(
                    id=user.id,
                    user_id=user.user_id,
                    chat_room_id=user.chat_room_id,
                    joined_at=datetime.fromtimestamp(user.joined_at.seconds)
                )
                for user in user_response.users
            ]

            # Fetch messages from the chat room
            message_request = GetMessagesByChatRoomIdRequest(chat_room_id=id)
            message_response = message_client.GetMessagesByChatRoomId(message_request)

            messages = [
                ChatRoomMessageType(
                    id=msg.id,
                    content=msg.content,
                    sender_id=msg.sender_id,
                    chat_room_id=msg.chat_room_id,
                    timestamp=datetime.fromtimestamp(msg.timestamp.seconds)
                )
                for msg in message_response.messages
            ]

            # Simulate fetching chat room details (e.g., room name or creation date)
            # Extend this part to include details from an actual ChatRoom gRPC if necessary.
            # Current implementation provides only ID and mock 'name'/'created_at'.
            return ChatRoomType(
                id=id,
                name=f"Chat Room {id}",
                created_at=datetime.utcnow(),
                users=users,
                messages=messages
            )

        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code().name})")
        except Exception as ex:
            raise Exception(f"Unexpected error: {str(ex)}")

class Mutation(graphene.ObjectType):
    manage_chat = ManageChatMutation.Field()


# GraphQL Schema
schema = graphene.Schema(query=Query, mutation=Mutation)
