import os
import channels
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from main_service.consumer import MyGraphqlWsConsumer
from main_service.api.schema.chatSchema import ChatRoomMessageSubscription

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_service.settings')

django_asgi_app = get_asgi_application()

django.setup()

application = channels.routing.ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            channels.routing.URLRouter(
                [
                    path("graphql/", MyGraphqlWsConsumer.as_asgi()),
                ]
            )
        ),
    }
)
