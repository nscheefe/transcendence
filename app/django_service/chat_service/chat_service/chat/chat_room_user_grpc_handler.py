import google
import grpc
from django.utils.timezone import now
from chat_service.protos import ChatRoomUser_pb2_grpc, ChatRoomUser_pb2
from chat_service.chat.models import ChatRoom, ChatRoomUser


class ChatRoomUserServiceHandler(ChatRoomUser_pb2_grpc.ChatRoomUserServiceServicer):
    """Implementation of ChatRoomUserService."""

    def __init__(self):
        pass

    def AddUserToChatRoom(self, request, context):
        """
        Adds a user to a chat room.
        """
        try:
            # Validate if the ChatRoom exists
            chat_room = ChatRoom.objects.get(id=request.chat_room_id)

            # Create or ensure the user is added to the ChatRoom
            chat_room_user, created = ChatRoomUser.objects.get_or_create(
                user_id=request.user_id,
                chat_room=chat_room,
                defaults={"joined_at": now()},
            )

            # Prepare response protobuf with joined_at timestamp
            joined_at = google.protobuf.timestamp_pb2.Timestamp()
            joined_at.FromDatetime(chat_room_user.joined_at)

            return ChatRoomUser_pb2.ChatRoomUser(
                id=chat_room_user.id,
                user_id=chat_room_user.user_id,
                chat_room_id=chat_room_user.chat_room.id,
                joined_at=joined_at,
            )
        except ChatRoom.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Chat room not found")
            return ChatRoomUser_pb2.ChatRoomUser()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error adding user to chat room: {str(e)}")
            return ChatRoomUser_pb2.ChatRoomUser()

    def GetUsersByChatRoomId(self, request, context):
        """
        Retrieves all users in a specific chat room by its ID.
        """
        try:
            # Validate if the ChatRoom exists
            chat_room = ChatRoom.objects.get(id=request.chat_room_id)

            # Fetch all ChatRoomUser entries for the ChatRoom
            chat_room_users = ChatRoomUser.objects.filter(chat_room=chat_room)

            # Build response protobuf
            response = ChatRoomUser_pb2.ListChatRoomUsersResponse()
            for user in chat_room_users:
                joined_at = google.protobuf.timestamp_pb2.Timestamp()
                joined_at.FromDatetime(user.joined_at)

                response.users.add(
                    id=user.id,
                    user_id=user.user_id,
                    chat_room_id=user.chat_room.id,
                    joined_at=joined_at,
                )

            return response
        except ChatRoom.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Chat room not found")
            return ChatRoomUser_pb2.ListChatRoomUsersResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching users in chat room: {str(e)}")
            return ChatRoomUser_pb2.ListChatRoomUsersResponse()

    @classmethod
    def as_servicer(cls):
        """
        Returns a servicer instance of this class.
        """
        return cls()
