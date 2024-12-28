import google
import grpc
from django.utils.timezone import now
from chat_service.protos import chat_pb2_grpc, chat_pb2
from chat_service.chat.models import ChatRoom, ChatRoomMessage


class ChatServiceHandler(chat_pb2_grpc.ChatServiceServicer):
    """Implementation of ChatService."""

    def __init__(self):
        pass

    def CreateChatRoom(self, request, context):
        """
        Creates a new ChatRoom.
        """
        try:
            chat_room = ChatRoom(
                name=request.name,
                game_id=request.game_id
            )
            chat_room.save()

            # Prepare the response using ChatRoom proto
            created_at = google.protobuf.timestamp_pb2.Timestamp()
            created_at.FromDatetime(chat_room.created_at)

            return chat_pb2.ChatRoom(
                id=chat_room.id,
                name=chat_room.name,
                created_at=created_at,
                game_id=chat_room.game_id,
            )
        except Exception as e:
            context.set_details(f"Error creating chat room: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return chat_pb2.ChatRoom()  # Empty response in case of failure

    def GetChatRoomById(self, request, context):
        """
        Retrieves a ChatRoom by its ID.
        """
        try:
            # Fetch the ChatRoom by ID or raise a 404 if not found
            chat_room = ChatRoom.objects.get(id=request.id)

            created_at = google.protobuf.timestamp_pb2.Timestamp()
            created_at.FromDatetime(chat_room.created_at)

            return chat_pb2.ChatRoom(
                id=chat_room.id,
                name=chat_room.name,
                created_at=created_at,
                game_id=chat_room.game_id,
            )
        except ChatRoom.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Chat room not found")
            return chat_pb2.ChatRoom()  # Empty response for not found

    def ListChatRooms(self, request, context):
        """
        Streams all available ChatRooms.
        """
        try:
            chat_rooms = ChatRoom.objects.all()  # Retrieve all chat rooms

            for chat_room in chat_rooms:
                created_at = google.protobuf.timestamp_pb2.Timestamp()
                created_at.FromDatetime(chat_room.created_at)

                # Yield a response for each ChatRoom (streaming RPC)
                yield chat_pb2.ChatRoom(
                    id=chat_room.id,
                    name=chat_room.name,
                    created_at=created_at,
                    game_id=chat_room.game_id,
                )
        except Exception as e:
            context.set_details(f"Error listing chat rooms: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)

    def CreateChatMessage(self, request, context):
        """
        Stores a message within a ChatRoom.
        """
        try:
            # Check if the ChatRoom exists
            chat_room = ChatRoom.objects.get(id=request.chat_room_id)

            # Save the message
            message = ChatRoomMessage(
                content=request.content,
                sender_id=request.sender_id,
                chat_room=chat_room,
            )
            message.save()

            # Prepare timestamp from saved message
            timestamp = google.protobuf.timestamp_pb2.Timestamp()
            timestamp.FromDatetime(message.timestamp)

            # Return the message as response
            return chat_pb2.ChatMessage(
                id=message.id,
                content=message.content,
                sender_id=message.sender_id,
                chat_room_id=message.chat_room_id,
                timestamp=timestamp,
            )
        except ChatRoom.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Chat room not found")
            return chat_pb2.ChatMessage()
        except Exception as e:
            context.set_details(f"Error creating chat message: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return chat_pb2.ChatMessage()

    @classmethod
    def as_servicer(cls):
        """
        Returns a servicer instance of this class.
        """
        return cls()
