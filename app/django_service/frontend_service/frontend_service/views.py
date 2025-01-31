from pprint import pprint

from venv import logger
from django.shortcuts import render, redirect
from django.conf import settings

from .logic.commonContext import get_home_context
from .logic.auth.utils import jwt_required, isJwtSet
from .logic.auth.sign_in import signIn, exchange_code_for_token
from .logic.gql.query.get_user_data import getUserProfileData
from .logic.gql.query.get_user_chat import getDetailedChatRoomData
from .logic.gql.query.get_profile_data import getProfileData
from .logic.gql.mutation import update_profile , create_game
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import os
import jwt

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
    response.set_cookie('jwt_token', access_token, httponly=True, secure=settings.SECURE_COOKIE, samesite='None')
    return response

@jwt_required
def home(request):
    # Create context dictionary with necessary data
    context = get_home_context(request)
    return render(request, 'frontend/home.html', context)

def home2(request):
    return render(request, 'frontend/homeNils.html')

@jwt_required
def game(request):
    context = get_home_context(request)
    game = None
    # Check for the 'local' query parameter
    is_local_game = request.GET.get('local', 'false').lower() == 'true'
    if is_local_game != True:
        game = create_game.createGame(request)
        logger.info(game)

    # Extend the context with additional data for the game view
    context.update({
        'game': game,  # Example function for getting game data
        'is_local_game': is_local_game,  # Add the local game flag to the context
    })

    return render(request, 'frontend/pong.html', context)

@csrf_exempt
@jwt_required
def profile(request):
    user_data = getUserProfileData(request)
    context = {
        'show_nav': True,
        'user': user_data,
    }
    if request.method == 'POST':
        bio = request.POST.get('Bio')
        nickname = request.POST.get('Nickname')
        avatar = request.FILES.get('filename')
        additional_info = request.POST.get('additionalInfo')
        token = request.COOKIES.get('jwt_token')

        avatar_path = user_data['profile']['avatarUrl']
        if avatar:
            try:
                decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
                user_id = decoded_token.get('user_id')
            except jwt.ExpiredSignatureError:
                return JsonResponse({'success': False, 'message': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'success': False, 'message': 'Invalid token'}, status=401)
            except jwt.InvalidSignatureError:
                return JsonResponse({'success': False, 'message': 'Signature verification failed'}, status=401)
            user_upload_dir = os.path.join(settings.MEDIA_ROOT, 'avatars', str(user_id))

            if not os.path.exists(user_upload_dir):
                os.makedirs(user_upload_dir)

            # Delete old avatar if it exists
            for filename in os.listdir(user_upload_dir):
                file_path = os.path.join(user_upload_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            avatar_path = default_storage.save(os.path.join('avatars', str(user_id), avatar.name), ContentFile(avatar.read()))
            avatar_path = default_storage.url(avatar_path)

        response = update_profile.manageProfile(request, bio, nickname, avatar_path, additional_info)
        return JsonResponse(response)

    return render(request, 'frontend/manage-profile.html', context)

#@csrf_exempt
#def upload_avatar(request):
#    if request.method == 'POST' and request.FILES.get('filename'):
#        token = request.COOKIES.get('jwt_token')
#        if not token:
#            return JsonResponse({'success': False, 'message': 'Authentication token is missing'}, status=401)

#        try:
#            decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
#            user_id = decoded_token.get('user_id')
#        except jwt.ExpiredSignatureError:
#            return JsonResponse({'success': False, 'message': 'Token has expired'}, status=401)
#        except jwt.InvalidTokenError:
#            return JsonResponse({'success': False, 'message': 'Invalid token'}, status=401)
#        except jwt.InvalidSignatureError:
#            return JsonResponse({'success': False, 'message': 'Signature verification failed'}, status=401)

#        avatar_file = request.FILES['filename']
#        user_upload_dir = os.path.join(settings.MEDIA_ROOT, 'avatars', str(user_id))

#        if not os.path.exists(user_upload_dir):
#            os.makedirs(user_upload_dir)

#        # Delete old avatar if it exists
#        for filename in os.listdir(user_upload_dir):
#            file_path = os.path.join(user_upload_dir, filename)
#            if os.path.isfile(file_path):
#                os.remove(file_path)

#        file_name = default_storage.save(os.path.join('avatars', str(user_id), avatar_file.name), ContentFile(avatar_file.read()))
#        file_url = default_storage.url(file_name)
#        return JsonResponse({'success': True, 'url': file_url})
#    return JsonResponse({'success': False, 'message': 'File upload failed'}, status=400)

@jwt_required
def stats(request):
    user_data = getUserProfileData(request)

    context = {
        'show_nav': True,
        'user': user_data,

    }
    return render(request, 'frontend/Leaderboard.html', context)

@jwt_required
def tournament(request):
    user_data = getUserProfileData(request)
    context = {
        'show_nav': True,
        'user': user_data,

    }
    return render(request, 'frontend/tournament.html', context)


@jwt_required
def community(request):
    user_data = getUserProfileData(request)
    context = {
        'show_nav': True,
        'user': user_data,
        #'friends_data': get_user_friends(request.user),  # Example function for getting friends data
    }
    return render(request, 'frontend/community.html', context)


@jwt_required
def chat(request):
    user_data = getUserProfileData(request)
    ChatRooms = getDetailedChatRoomData(request)
    context = {
        'show_nav': True,
        'user': user_data,
    }
    pprint(ChatRooms)

    return render(request, 'frontend/chat.html', context)

@jwt_required
def publicProfile(request, user_id):
    # Example: Fetch data or log the user_id
    referrer = request.META.get('HTTP_REFERER', None)
    print(f"User ID is: {user_id}")
    profile_data = getProfileData(request, user_id)
    user_data = getUserProfileData(request)
    context = {
        'show_nav': True,
        'user': user_data,
        'userProfileId': user_id,
        'profile': profile_data,
        'referrer': referrer,  # Add referrer to the context if needed
    }
    return render(request, 'frontend/publicProfile.html', context)




def pong_view(request):
    return render(request, 'frontend/pong.html')
