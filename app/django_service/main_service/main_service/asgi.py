import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from main_service.api.schema import Schema
from main_service.api.middleware.authMiddleware import AuthMiddlewareStack
from ariadne.asgi import GraphQL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_service.settings')

django_asgi_app = get_asgi_application()

django.setup()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("graphql/", GraphQL(Schema.schema)),
            path("graphql", GraphQL(Schema.schema)),
        ])
    ),
})
