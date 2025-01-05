from django.shortcuts import render, redirect
from django.conf import settings
from .logic.auth.utils import jwt_required, isJwtSet
from .logic.auth.sign_in import signIn, exchange_code_for_token
from .logic.query.gql.get_user_data import getUserProfileData

def root_redirect(request):
    """
    Redirect the user based on authentication status.
    """
    if isJwtSet(request):
        return redirect('home')
    return redirect('signin')

def signin(request):
    context = signIn(request)
    return render(request, 'frontend/sign-in.html', context)

def signout(request):
    response = redirect('signin')
    response.delete_cookie('jwt')
    return response

def oauth_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if not code or not state:
        return render(request, 'frontend/error.html', {'error': 'No code or state provided'})

    # Call the GraphQL mutation to exchange the code for a token
    token_data = exchange_code_for_token(code, state)

    if 'errors' in token_data:
        return render(request, 'frontend/error.html', {'error': 'Failed to obtain access token'})

    if 'exchangeCodeForToken' not in token_data:
        return render(request, 'frontend/error.html', {'error': 'Invalid response from server'})

    access_token = token_data['exchangeCodeForToken']['jwtToken']

    # Store the JWT as a cookie
    response = redirect('home')
    response.set_cookie('jwt_token', access_token, httponly=True, secure=settings.SECURE_COOKIE, samesite='Lax')
    return response

@jwt_required
def home(request):
    # Create context dictionary with necessary data
    user_data = getUserProfileData(request)
    context = {
        'show_nav': True,
        'user_name': request.user.username,  # Example: passing the username
        'user': user_data,
    }
    return render(request, 'frontend/home.html', context)

@jwt_required
def profile(request):
    context = {
        'show_nav': True,
        'user': getUserProfileData(request),  # Example function for getting profile data
    }
    return render(request, 'frontend/manage-profile.html', context)

@jwt_required
def stats(request):
    context = {
        'show_nav': True,
        'stats_data': get_user_stats(request.user),  # Example function for getting stats data
    }
    return render(request, 'frontend/stats.html', context)

@jwt_required
def friends(request):
    context = {
        'user_name': request.user.username,
        'friends_data': get_user_friends(request.user),  # Example function for getting friends data
    }
    return render(request, 'frontend/friends.html', context)

@jwt_required
def game(request):
    context = {
        'user_name': request.user.username,
        'game_data': get_game_data(request.user),  # Example function for getting game data
    }
    return render(request, 'frontend/game.html', context)
