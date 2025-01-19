from datetime import datetime, time
import logging
from math import log
import re
import google
import grpc
from concurrent import futures
from django_socio_grpc import generics, proto_serializers
from django_socio_grpc.decorators import grpc_action
from django_socio_grpc.mixins import AsyncStreamModelMixin
from django.utils.timezone import now
from asgiref.sync import async_to_sync
from google.protobuf.timestamp_pb2 import Timestamp
from rest_framework import serializers
from chat_service.protos import chat_pb2, chat_pb2_grpc
from app.django_service.chat_service.chat_service.chat.models import ChatRoom, ChatRoomMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
import queue

logger = logging.getLogger(__name__)

class ChatServiceHandler(chat_pb2_grpc.ChatServiceServicer):
    """Implementation of ChatService."""

    def __init__(self):
        self.message_queues = {}

    def CreateChatRoom(self, request, context):
        """
        Creates a new ChatRoom.
        """
        try:
            chat_room = ChatRoom(
                name=request.name,
                game_id=request.game_id,
                created_at=datetime.now()
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

    @classmethod
    def as_servicer(cls):
        """
        Returns a servicer instance of this class.
        """
        return cls()

class ChatRoomMessageSerializer(proto_serializers.ModelProtoSerializer):
    """
    Serializer for ChatRoomMessage model.
    """
    class Meta:
        model = ChatRoomMessage
        fields = '__all__'
        proto_class = chat_pb2.ChatRoomMessage
        proto_class_list = chat_pb2.ListChatRoomMessagesResponse

class ChatStreamService(generics.AsyncModelService, AsyncStreamModelMixin):
    """
    Streams messages from a chat room.
    """
    #queryset = ChatRoomMessage.objects.all()
    #filter_backends = ['chat_room_id']
    #serializer_class = ChatRoomMessageSerializer
    #@grpc_action(
    #    request=[{"chat_room_id": "int"}],
    #    response=[{"chat_room_id": "int", "user_id": "int", "message": "string", "timestamp": "Timestamp"}],
    #    response_stream=True,
    #)
    async def SubscribeChatRoomMessages(self, request, context):
        logger.debug(f"Subscribing to chat room messages for chat room ID: {request.chat_room_id}")
        chat_room_id = request.chat_room_id
        # Create a queue for this chat room if it doesn't exist
        if chat_room_id not in self.message_queues:
            self.message_queues[chat_room_id] = queue.Queue()
        # Stream existing messages
        messages = ChatRoomMessage.objects.filter(chat_room_id=chat_room_id).order_by('timestamp')
        async for message in request:
            timestamp = Timestamp()
            timestamp.FromDatetime(message.timestamp)
            yield chat_pb2.ChatMessage(
                chat_room_id=message.chat_room_id,
                user_id=message.user_id,
                message=message.message,
                timestamp=timestamp
            )
        # Stream new messages
        while True:
            try:
                message = self.message_queues[chat_room_id].get_nowait()
                timestamp = Timestamp()
                timestamp.FromDatetime(message.timestamp)
                yield chat_pb2.ChatMessage(
                    chat_room_id=message.chat_room_id,
                    user_id=message.user_id,
                    message=message.message,
                    timestamp=timestamp
                )
            except queue.Empty:
                time.sleep(1)  # Sleep for a second and continue
                continue

    #   async for message in messages:
    #       timestamp = Timestamp()
    #       timestamp.FromDatetime(message.timestamp)
    #       yield chat_pb2.ChatMessage(
    #           chat_room_id=message.chat_room_id,
    #           user_id=message.user_id,
    #           message=message.message,
    #           timestamp=timestamp
    #       )
    #   # Stream new messages
    #   while True:
    #       try:
    #           message = self.message_queues[chat_room_id].get_nowait()
    #           timestamp = Timestamp()
    #           timestamp.FromDatetime(message.timestamp)
    #           yield chat_pb2.ChatMessage(
    #               chat_room_id=message.chat_room_id,
    #               user_id=message.user_id,
    #               message=message.message,
    #               timestamp=timestamp
    #           )
    #       except queue.Empty:
    #           time.sleep(1)  # Sleep for a second and
    #           continue

# Signal receiver to listen for new messages and add them to the queue
@receiver(post_save, sender=ChatRoomMessage)
def new_message_handler(sender, instance, created, **kwargs):
    if created:
        chat_room_id = instance.chat_room_id
        if chat_room_id in ChatServiceHandler().message_queues:
            ChatServiceHandler().message_queues[chat_room_id].put(instance)

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def SubscribeChatRoomMessages(self, request, context):
        chat_room_id = request.chat_room_id
        # Stream messages for the given chat room ID
        while True:
            # Fetch messages from the database or other source
            messages = ChatRoomMessage.objects.filter(chat_room_id=chat_room_id).order_by('timestamp')
            for message in messages:
                timestamp = Timestamp()
                timestamp.FromDatetime(message.timestamp)
                yield chat_pb2.ChatMessage(
                    id=message.id,
                    content=message.content,
                    sender_id=message.sender_id,
                    chat_room_id=message.chat_room_id,
                    timestamp=timestamp
                )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
