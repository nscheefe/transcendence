import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.auth import AuthMiddlewareStack
from .consumer import MyGraphqlWsConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main_service.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter(
            [
                path("graphql/", MyGraphqlWsConsumer.as_asgi()),
            ]
        ),
    }
)
