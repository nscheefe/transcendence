#import channels_graphql_ws

#import graphql
#import graphene
from .api.schema.Schema import schema
#from .api.schema.chatSchema import ChatRoomMessageSubscription
import json
from ariadne.asgi import GraphQL
from channels.generic.websocket import WebsocketConsumer
from channels.routing import URLRouter
from django.urls import path, re_path


class MyGraphqlWsConsumer(WebsocketConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""
    #send_ping_every = 2
    schema = GraphQL(schema, debug=True)
