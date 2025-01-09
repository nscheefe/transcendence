import channels_graphql_ws

import graphql
import graphene
from .api.schema.Schema import Query, Mutation, Subscription
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

    send_ping_every = 1
    schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
    middleware = [demo_middleware]
