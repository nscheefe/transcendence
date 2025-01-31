import asyncio
import grp
from urllib import response
from django_socio_grpc import generics, mixins
from .models import ChatRoom, ChatRoomMessage, ChatRoomUser
from .serializers import ChatRoomProtoSerializer, ChatRoomMessageProtoSerializer, ChatRoomUserProtoSerializer
from django_socio_grpc.decorators import grpc_action
from django_socio_grpc.protobuf.generation_plugin import ListGenerationPlugin
from asgiref.sync import sync_to_async
from google.protobuf.json_format import ParseDict
from chat_service.chat.grpc import chat_pb2, chat_pb2_grpc
from chat_service.chat.grpc.chat_pb2 import ChatRoomMessageResponse, ChatRoomResponse  # Import the correct gRPC message class
import logging
from django_socio_grpc.exceptions import NotFound

logger = logging.getLogger('django_socio_grpc')


class ChatRoomService(generics.AsyncModelService):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomProtoSerializer

    @grpc_action(request=[{"name": "user_id", "type": "int32"}],
                 response=ChatRoomProtoSerializer,
                 response_stream=True)
    async def GetChatRoomByUserId(self, request, context):
        """
        gRPC action to retrieve chat rooms associated with a specific user.

        Args:
            request: The request object containing the user_id for which to fetch chat rooms.
            context: The gRPC context for the call.

        Yields:
            Serialized chat room data for each chat room associated with the specified user.
        """
        user_id = request.user_id
        last_chat_rooms = set()

        while True:
            # Fetch chat rooms where the specified user is a participant
            chat_rooms = await sync_to_async(list)(ChatRoom.objects.filter(participants__user_id=user_id))

            # Convert chat rooms to a set of IDs for comparison
            current_chat_rooms = set(chat_room.id for chat_room in chat_rooms)

            # Check for new or updated chat rooms
            new_or_updated_chat_rooms = current_chat_rooms - last_chat_rooms

            for chat_room in chat_rooms:
                if chat_room.id in new_or_updated_chat_rooms:
                    serialized_message = await sync_to_async(lambda: self.serializer_class(chat_room).data)()
                    yield ParseDict(serialized_message, ChatRoomResponse())

            # Update the last chat rooms set
            last_chat_rooms = current_chat_rooms

            # Sleep for a while before checking for updates again
            await asyncio.sleep(5)

class ChatRoomMessageService(generics.AsyncModelService):
    queryset = ChatRoomMessage.objects.all()
    serializer_class = ChatRoomMessageProtoSerializer
    filter_set = {"chat_room_id": "chat_room_id"}

    @grpc_action(request=[{"name": "chat_room_id", "type": "int32"}], response=ChatRoomMessageProtoSerializer, response_stream=True)
    async def SubscribeChatRoomMessages(self, request, context):
        chat_room_id = request.chat_room_id
        last_message_id = None

        # Create an async generator to yield messages
        async def message_generator():
            nonlocal last_message_id
            while True:
                # Fetch new messages from the database
                if last_message_id is None:
                    messages = await sync_to_async(list)(self.queryset.filter(chat_room_id=chat_room_id))
                else:
                    messages = await sync_to_async(list)(self.queryset.filter(chat_room_id=chat_room_id, id__gt=last_message_id))

                for message in messages:
                    serialized_message = self.serializer_class(message).data
                    grpc_message = ParseDict(serialized_message, ChatRoomMessageResponse())
                    yield grpc_message
                    last_message_id = message.id

                # Sleep for a short period before checking for new messages again
                await asyncio.sleep(1)

        # Use the async generator to yield messages
        async for message in message_generator():
            yield message

class ChatRoomUserService(generics.AsyncModelService):
    queryset = ChatRoomUser.objects.all()
    serializer_class = ChatRoomUserProtoSerializer

