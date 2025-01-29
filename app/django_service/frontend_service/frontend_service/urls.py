from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.root_redirect, name='root_redirect'),  # Root route redirection
    path('signin/', views.signin, name='signin'),  # Sign-in view
    path('signout/', views.signout, name='signout'),  # Sign-out view
    path('oauth_callback/', views.oauth_callback, name='oauth_callback'),  # OAuth callback view

    # If the user is not authenticated, they will be redirected to the sign-in page.
    path('home/', views.home, name='home'),  # Main home view
    path('home/stats/', views.stats, name='stats'),  # Stats view
    path('home/community/', views.community, name='community'),  # Friends view
    path('home/game/', views.game, name='game'),  # Game view
    #path('home/game/', views.game, name='game'),  # Game view
    path('home/profile/', views.profile, name='profile'),  # Profile view
    path('home/profile/<int:user_id>/', views.publicProfile, name='publicProfile'),
    path('home/chat/', views.chat, name='chat'),  # chat view
    path('home/tournaments/', views.tournament, name='tournament'),  # chat view
    path('home2/', views.home2, name='home2'),  #REMOVE

                  # Game
    path('home/game/', views.game, name='game'),  # Start game view

    #path('upload-avatar/', views.upload_avatar, name='upload_avatar'),  # File upload view
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
