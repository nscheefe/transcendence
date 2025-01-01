from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def root_redirect(request):
    """
    Redirect the user based on authentication status.
    """
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('signin')

def signin(request):
    # Here you would typically handle your signin logic (form submission, validation, etc.)
    return render(request, 'frontend/sign-in.html')

@login_required
def home(request):
    # Create context dictionary with necessary data
    context = {
        'show_nav': True,
        'user_name': request.user.username,  # Example: passing the username
    }
    return render(request, 'frontend/home.html', context)

@login_required
def profile(request):
    context = {
        'user_name': request.user.username,
        'profile_data': get_user_profile_data(request.user),  # Example function for getting profile data
    }
    return render(request, 'frontend/profile.html', context)

@login_required
def stats(request):
    context = {
        'user_name': request.user.username,
        'stats_data': get_user_stats(request.user),  # Example function for getting stats data
    }
    return render(request, 'frontend/stats.html', context)

@login_required
def friends(request):
    context = {
        'user_name': request.user.username,
        'friends_data': get_user_friends(request.user),  # Example function for getting friends data
    }
    return render(request, 'frontend/friends.html', context)

@login_required
def game(request):
    context = {
        'user_name': request.user.username,
        'game_data': get_game_data(request.user),  # Example function for getting game data
    }
    return render(request, 'frontend/game.html', context)
