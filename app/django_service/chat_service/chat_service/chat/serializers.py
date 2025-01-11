from django_socio_grpc import proto_serializers
from rest_framework import serializers
from .models import ChatRoom, ChatRoomMessage, ChatRoomUser

class ChatRoomProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ChatRoom
        fields = "__all__"

class ChatRoomMessageProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ChatRoomMessage
        fields = "__all__"

class ChatRoomUserProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = ChatRoomUser
        fields = "__all__"
