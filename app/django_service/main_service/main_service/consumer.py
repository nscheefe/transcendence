import channels_graphql_ws

import graphql
import graphene
from .api.schema.Schema import Query, Mutation, Subscription
from .api.schema.chatSchema import ChatRoomMessageSubscription
import json

async def demo_middleware(next_middleware, root, info, *args, **kwds):
    print("Demo middleware report")
    print("    operation :", info.operation.operation)
    print("    name      :", info.operation.name.value)

    # Invoke next middleware.
    result = next_middleware(root, info, *args, **kwds)
    if graphql.pyutils.is_awaitable(result):
        result = await result

    # Ensure the result is async iterable.
    if not hasattr(result, "__aiter__"):
        raise TypeError(
            f"Middleware must return an async iterable or observable! Got: {type(result)}"
        )
    return result


class MyGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""

    #send_ping_every = 1
    schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
    middleware = [demo_middleware]
    async def on_connect(self, payload):
        """New client connection handler."""
        # Handle connection logic
        print("New client connected!")

    async def on_receive(self, text_data):
        # Parse the received data to get the chat_room_id
        data = json.loads(text_data)
        chat_room_id = data.get("chat_room_id")

        # Call the subscribe_chat_room_messages function
        await ChatRoomMessageSubscription.subscribe_chat_room_messages(chat_room_id)

    async def on_disconnect(self, code):
        # Handle disconnection logic
        pass

    async def new_chat_message(self, chat_room_id, payload):
        # Send the new chat message to the WebSocket client
        await self.send_json({
            "chat_room_id": chat_room_id,
            "message": payload
        })
