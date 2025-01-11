from django_socio_grpc import proto_serializers
from rest_framework import serializers
from .models import ChatRoom, ChatRoomMessage, ChatRoomUser
from chat_service.chat.grpc.chat_pb2 import (
    ChatRoomListResponse,
    ChatRoomMessageListResponse,
    ChatRoomUserListResponse,
    ChatRoomResponse,
    ChatRoomMessageResponse,
    ChatRoomUserResponse,
)

class ChatRoomProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ChatRoom
        proto_class = ChatRoomResponse
        proto_class_list = ChatRoomListResponse
        fields = "__all__"


class ChatRoomMessageProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ChatRoomMessage
        proto_class = ChatRoomMessageResponse
        proto_class_list = ChatRoomMessageListResponse
        fields = "__all__"

class ChatRoomUserProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ChatRoomUser
        proto_class = ChatRoomUserResponse
        proto_class_list = ChatRoomUserListResponse
        fields = "__all__"
