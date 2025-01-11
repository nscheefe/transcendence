from django_socio_grpc import generics, mixins
from .models import ChatRoom, ChatRoomMessage, ChatRoomUser
from .serializers import ChatRoomProtoSerializer, ChatRoomMessageProtoSerializer, ChatRoomUserProtoSerializer
from django_socio_grpc.decorators import grpc_action

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

    @grpc_action(request=[{"name": "chat_room_id", "type": "int32"}], response=ChatRoomMessageProtoSerializer, response_stream=True)
    async def SubscribeChatRoomMessages(self, request, context):
        chat_room_id = request.chat_room_id
        messages = self.queryset.filter(chat_room_id=chat_room_id)
        for message in messages:
            yield self.serializer_class(message).data

class ChatRoomUserService(generics.AsyncModelService):
    queryset = ChatRoomUser.objects.all()
    serializer_class = ChatRoomUserProtoSerializer

    @grpc_action(request=[{"name": "user_id", "type": "int32"}], response=ChatRoomProtoSerializer, response_stream=True)
    async def GetChatRoomByUserId(self, request, context):
        user_id = request.user_id
        chat_rooms = ChatRoom.objects.filter(participants__user_id=user_id)
        for chat_room in chat_rooms:
            yield ChatRoomProtoSerializer(chat_room).data
