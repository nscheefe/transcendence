import os
import channels
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from main_service.consumer import MyGraphqlWsConsumer
from main_service.api.schema.chatSchema import ChatRoomMessageSubscription

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_service.settings')

application = channels.routing.ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            channels.routing.URLRouter(
                [
                    path("graphql/", MyGraphqlWsConsumer.as_asgi()),
                ]
            )
        ),
    }
)
