"""
URL configuration for main_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt

from main_service.api.schema import Schema as MainSchema
from main_service.api.schema.authSchema import schemaAuth
from .views import CustomGraphQLView, graphiql

from . import settings

urlpatterns = [
    django.urls.path("", graphiql),
    #path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=MainSchema.schema))),  # GraphQL API endpoint
    path('graphql-ws/', csrf_exempt(CustomGraphQLView.as_view(graphiql=True, schema=MainSchema.schema))),  # Subscription endpoint
    path('graphiql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=MainSchema.schema))),  # GraphiQL frontend
    path('auth/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schemaAuth))),  # Auth GraphQL API endpoint
]

if settings.DEBUG:  # Only serve static files in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
