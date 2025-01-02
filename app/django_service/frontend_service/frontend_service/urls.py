from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='sign-in'),  # Default route for '/'
	path('home/', views.home, name='home'),  # Route for '/home/'
	path('register/', views.register, name='register'),  # Route for '/register/'

]
