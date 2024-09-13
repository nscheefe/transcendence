"""
URL configuration for stat_service project.

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
from django.contrib import admin
from django.urls import path

from .protos import stat_pb2_grpc
from .stats.grpc_handlers import StatServiceHandler

urlpatterns = [
]


def grpc_handlers(server):
    stat_service_handler = StatServiceHandler.as_servicer()
    stat_pb2_grpc.add_StatServiceServicer_to_server(stat_service_handler, server)