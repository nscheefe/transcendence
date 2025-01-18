import os
import channels
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from main_service.api.schema import Schema
#from main_service.api.schema.chatSchema import ChatRoomMessageSubscription

from ariadne.asgi import GraphQL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_service.settings')

django_asgi_app = get_asgi_application()

django.setup()

application = channels.routing.ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            channels.routing.URLRouter(
                [
                    django.urls.path("graphql/", GraphQL(Schema.schema)),
                ]
            )
        ),
    }
)

#from ariadne.asgi import GraphQL
#from channels.http import AsgiHandler
#from channels.routing import URLRouter
#from django.urls import path, re_path


#schema = ...


#application = URLRouter([
#    path("graphql/", GraphQL(schema, debug=True)),
#    re_path(r"", AsgiHandler),
#])
