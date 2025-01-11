import asyncio
from urllib import response
from django_socio_grpc import generics, mixins
from .models import ChatRoom, ChatRoomMessage, ChatRoomUser
from .serializers import ChatRoomProtoSerializer, ChatRoomMessageProtoSerializer, ChatRoomUserProtoSerializer
from django_socio_grpc.decorators import grpc_action
from asgiref.sync import sync_to_async
from google.protobuf.json_format import ParseDict
from chat_service.chat.grpc import chat_pb2, chat_pb2_grpc
from chat_service.chat.grpc.chat_pb2 import ChatRoomMessageResponse  # Import the correct gRPC message class

class ChatRoomService(generics.AsyncModelService):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomProtoSerializer

    @grpc_action(request=[], response=ChatRoomProtoSerializer, response_stream=True)
    async def ListChatRooms(self, request, context):
        for chat_room in self.queryset:
            yield self.serializer_class(chat_room).data

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

    @grpc_action(request=[{"name": "user_id", "type": "int32"}], response=ChatRoomProtoSerializer, response_stream=True)
    async def GetChatRoomByUserId(self, request, context):
        user_id = request.user_id
        chat_rooms = await sync_to_async(ChatRoom.objects.filter)(participants__user_id=user_id)
        for chat_room in await sync_to_async(list)(chat_rooms):
            yield ChatRoomProtoSerializer(chat_room).data
