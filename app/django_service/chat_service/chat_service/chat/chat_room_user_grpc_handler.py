import google
import grpc
import logging
from django.utils.timezone import now
from chat_service.protos import chat_pb2, chat_pb2_grpc
from chat_service.chat.models import ChatRoom, ChatRoomUser

from google.protobuf.timestamp_pb2 import Timestamp

logger = logging.getLogger(__name__)

class ChatRoomUserServiceHandler(chat_pb2_grpc.ChatRoomUserServiceServicer):
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

            return chat_pb2.ChatRoomUser(
                id=chat_room_user.id,
                user_id=chat_room_user.user_id,
                chat_room_id=chat_room_user.chat_room.id,
                joined_at=joined_at,
            )
        except ChatRoom.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Chat room not found")
            return chat_pb2.ChatRoomUser()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error adding user to chat room: {str(e)}")
            return chat_pb2.ChatRoomUser()

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
            response = chat_pb2.ListChatRoomUsersResponse()
            for user in chat_room_users:
                joined_at = google.protobuf.timestamp_pb2.Timestamp()
                joined_at.FromDatetime(user.joined_at)

                user_proto = response.users.add()
                user_proto.id = user.id
                user_proto.user_id = user.user_id
                user_proto.chat_room_id = user.chat_room.id
                user_proto.joined_at.CopyFrom(joined_at)

            return response
        except ChatRoom.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Chat room not found")
            return chat_pb2.ListChatRoomUsersResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching users in chat room: {str(e)}")
            return chat_pb2.ListChatRoomUsersResponse()

    def GetChatRoomByUserId(self, request, context):
        """
        Retrieves all chat rooms by a user ID.
        """
        try:
            logger.debug(f"Fetching chat rooms for user_id: {request.user_id}")

            # Fetch all chat rooms for the user
            chat_room_users = ChatRoomUser.objects.filter(user_id=request.user_id).select_related("chat_room")

            response = chat_pb2.ListChatRoomsResponse()

            if not chat_room_users.exists():
                logger.debug("No chat rooms found for the user")
                return response

            chat_rooms = {}
            for chat_room_user in chat_room_users:
                chat_room = chat_room_user.chat_room  # ForeignKey relationship

                if chat_room.id not in chat_rooms:
                    chat_room_proto = response.rooms.add()
                    chat_room_proto.id = chat_room.id
                    chat_room_proto.name = chat_room.name
                    chat_room_proto.created_at.FromDatetime(chat_room.created_at)
                    chat_room_proto.game_id = chat_room.game_id
                    chat_rooms[chat_room.id] = chat_room_proto

            logger.debug(f"Response: {response}")
            return response
        except ChatRoomUser.DoesNotExist:
            # Handle the case where no chat room users exist
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User is not part of any chat rooms")
            logger.error("User is not part of any chat rooms")
            return chat_pb2.ListChatRoomUsersResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching users in chat room: {str(e)}")
            logger.error(f"Error fetching users in chat room: {str(e)}")
            return chat_pb2.ListChatRoomUsersResponse()

    @classmethod
    def as_servicer(cls):
        """
        Returns a servicer instance of this class.
        """
        return cls()
