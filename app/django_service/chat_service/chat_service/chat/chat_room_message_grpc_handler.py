import google
import grpc
from django.utils.timezone import now
from chat_service.protos import chat_pb2, chat_pb2_grpc
from chat_service.chat.models import ChatRoom, ChatRoomMessage


class ChatRoomMessageServiceHandler(chat_pb2_grpc.ChatRoomMessageServiceServicer):
    """Implementation of ChatRoomMessageService."""

    def __init__(self):
        pass

    def CreateMessage(self, request, context):
        """
        Creates a new ChatRoomMessage for a chat room.
        """
        try:
            # Fetch the ChatRoom object by ID
            chat_room = ChatRoom.objects.get(id=request.chat_room_id)

            # Create the ChatRoomMessage object
            chat_room_message = ChatRoomMessage(
                content=request.content,
                sender_id=request.sender_id,
                chat_room=chat_room,
            )
            chat_room_message.save()

            # Prepare the response (convert timestamp format)
            timestamp = google.protobuf.timestamp_pb2.Timestamp()
            timestamp.FromDatetime(chat_room_message.timestamp)

            return chat_pb2.ChatRoomMessage(
                id=chat_room_message.id,
                content=chat_room_message.content,
                sender_id=chat_room_message.sender_id,
                chat_room_id=chat_room_message.chat_room.id,
                timestamp=timestamp,
            )
        except ChatRoom.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Chat room not found")
            return chat_pb2.ChatRoomMessage()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating chat room message: {str(e)}")
            return chat_pb2.ChatRoomMessage()

    def GetMessagesByChatRoomId(self, request, context):
        """
        Retrieves all messages for a specific ChatRoom by its ID.
        """
        try:
            # Fetch the ChatRoom object by ID
            chat_room = ChatRoom.objects.get(id=request.chat_room_id)

            # Retrieve all messages for the ChatRoom
            messages = ChatRoomMessage.objects.filter(chat_room=chat_room).order_by("timestamp")

            # Convert messages into protobuf response format
            response = chat_pb2.ListChatRoomMessagesResponse()
            for message in messages:
                # Prepare timestamp
                timestamp = google.protobuf.timestamp_pb2.Timestamp()
                timestamp.FromDatetime(message.timestamp)

                # Add each message to the response
                response.messages.add(
                    id=message.id,
                    content=message.content,
                    sender_id=message.sender_id,
                    chat_room_id=message.chat_room.id,
                    timestamp=timestamp,
                )

            return response
        except ChatRoom.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Chat room not found")
            return chat_pb2.ListChatRoomMessagesResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error fetching messages: {str(e)}")
            return chat_pb2.ListChatRoomMessagesResponse()

    @classmethod
    def as_servicer(cls):
        """
        Returns a servicer instance of this class.
        """
        return cls()
