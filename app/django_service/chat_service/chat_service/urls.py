"""
URL configuration for chat_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from chat_service.chat.grpc_handlers import ChatServiceHandler, ChatRoomMessageServiceHandler, ChatRoomUserServiceHandler
from .protos import chat_pb2_grpc
from .protos import ChatRoomUser_pb2_grpc
from .protos import ChatRoomMessage_pb2_grpc


urlpatterns = [
]



def grpc_handlers(server):
    # Register Chat Service
    chat_service_handler = ChatServiceHandler.as_servicer()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(chat_service_handler, server)

    # Register Chat Room Message Service
    chat_room_message_service_handler = ChatRoomMessageServiceHandler.as_servicer()
    ChatRoomMessage_pb2_grpc.add_ChatRoomMessageServiceServicer_to_server(chat_room_message_service_handler, server)

    # Register Chat Room User Service
    chat_room_user_service_handler = ChatRoomUserServiceHandler.as_servicer()
    ChatRoomUser_pb2_grpc.add_ChatRoomUserServiceServicer_to_server(chat_room_user_service_handler, server)
