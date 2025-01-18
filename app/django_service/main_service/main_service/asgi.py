from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import os
from django.urls import path
from .consumer import MyGraphqlWsConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main_service.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("graphql-ws/", MyGraphqlWsConsumer.as_asgi()),
                ]
            )
        ),
    }
)
