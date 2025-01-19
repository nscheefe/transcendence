"""
URL configuration for game_service project.

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
from .protos import game_pb2_grpc, tournament_pb2_grpc
from game_service.game.grpc_handlers import GameServiceHandler
from game_service.game.grpc_handlers import TournamentServiceHandler

urlpatterns = [
]




def grpc_handlers(server):
    game_service_handler = GameServiceHandler.as_servicer()
    game_pb2_grpc.add_GameServiceServicer_to_server(game_service_handler, server)
    tournament_service_handler = TournamentServiceHandler.as_servicer()
    tournament_pb2_grpc.add_TournamentServiceServicer_to_server(tournament_service_handler, server)
