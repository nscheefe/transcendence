import requests
from django.conf import settings

def exchange_code_for_token(code, state):
    token_url = "https://api.intra.42.fr/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
        'code': code,
        'state': state,
        'redirect_uri': settings.REDIRECT_URI,
    }
    response = requests.post(token_url, data=data)

    return response.json()

def get_user_info(access_token):
    user_info_url = "https://api.intra.42.fr/v2/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(user_info_url, headers=headers)
    return response.json()