import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime
import graphene

from main_service.protos.ChatRoomMessage_pb2_grpc import ChatRoomMessageServiceStub
from main_service.protos.ChatRoomMessage_pb2 import GetMessagesByChatRoomIdRequest, CreateChatRoomMessageRequest
from main_service.protos.chat_pb2 import CreateChatRoomRequest, GetChatRoomRequest
from main_service.protos.chat_pb2_grpc import ChatServiceStub
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
            client = ChatRoomUserServiceStub(channel)

            # Prepare and send the request
            request = GetUsersByChatRoomIdRequest(chat_room_id=self.id)
            response = client.GetUsersByChatRoomId(request)

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
                return []
            raise Exception(f"gRPC error: {e.details()} (Code: {str(e.code())})")

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
            chat_client = ChatServiceStub(channel)
            chat_request =  GetChatRoomRequest(id=id)
            chat_response = chat_client.GetChatRoomById(chat_request)

            user_request = GetUsersByChatRoomIdRequest(chat_room_id=id)
            user_response = user_client.GetUsersByChatRoomId(user_request)
            chat_room = ChatRoomType(id=id, name=chat_response.name, created_at=chat_response.created_at, game_id=chat_response.game_id)
            users = [
                ChatRoomUserType(
                    id=user.id,
                    user_id=user.user_id,
                    chat_room_id=user.chat_room_id,
                    joined_at=datetime.fromtimestamp(user.joined_at.seconds)
                )
                for user in user_response.users
            ]

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

            return ChatRoomType(
                id=chat_room.id,
                name=chat_room.name,
                created_at=datetime.fromtimestamp(chat_room.created_at.seconds),
                game_id=chat_room.game_id,
                users=users,
                messages=messages
            )

        except grpc.RpcError as e:
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
            stub = ChatRoomUserServiceStub(channel)

            request = AddUserToChatRoomRequest(
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
            stub = ChatRoomMessageServiceStub(channel)

            # Prepare the gRPC CreateChatRoomMessage request
            request = CreateChatRoomMessageRequest(
                chat_room_id=input["chat_room_id"],
                content=input["content"],
                sender_id=info.context.user_id
            )

            stub.CreateMessage(request)

            return CreateChatRoomMessageMutation(
                success=True,
                message="Message created successfully in the chat room."
            )
        except grpc.RpcError as e:
            return CreateChatRoomMessageMutation(
                success=False,
                message=f"gRPC error: {e.details()} (Code: {str(e.code())})"
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
            stub = ChatServiceStub(channel)

            request = CreateChatRoomRequest(
                name=input["name"],
                game_id=input["game_id"]
            )

            response = stub.CreateChatRoom(request)

            created_chat_room = ChatRoomType(
                id=response.id,
                name=response.name,
                created_at=response.created_at.ToDatetime(),
                game_id=response.game_id
            )
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

# GraphQL Schema
schema = graphene.Schema(query=Query, mutation=Mutation)
