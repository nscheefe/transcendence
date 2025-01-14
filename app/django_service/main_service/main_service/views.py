import pathlib
import django
from graphene_django.views import GraphQLView
import os
from django.conf import settings

class CustomGraphQLView(GraphQLView):
    graphiql_template = 'graphene-ws/graphiql.html'

    async def get_response(self, request, data, show_graphiql):
        # Execute the GraphQL query
        execution_result = await self.schema.execute_async(
            data.get('query'),
            variable_values=data.get('variables'),
            context_value=request,
            operation_name=data.get('operationName'),
        )

        # Check for errors in the execution result
        if execution_result.errors:
            return self.handle_errors(execution_result.errors)

        return self.format_response(execution_result)



def graphiql(request):
    """Trivial view to serve the `graphiql.html` file."""
    # It is important to create a session if it hasn't already been
    # created, because `sessionid` cookie is used to identify the
    # sender.
    if not request.session.session_key:
        request.session.create()
    del request
    graphiql_filepath = pathlib.Path(__file__).absolute().parent / 'templates/graphene-ws/graphiql.html'
    # It is better to specify an encoding when opening documents.
    # Using the system default implicitly can create problems on other
    # operating systems.
    with open(graphiql_filepath, encoding="utf-8") as f:
        return django.http.response.HttpResponse(f.read())
