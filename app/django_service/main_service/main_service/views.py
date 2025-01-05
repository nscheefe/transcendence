from graphene_django.views import GraphQLView
import os
from django.conf import settings

class CustomGraphQLView(GraphQLView):
    graphiql_template = 'graphene/graphiql.html'
