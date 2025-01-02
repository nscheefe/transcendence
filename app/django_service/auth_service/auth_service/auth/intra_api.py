import requests
from django.conf import settings
from datetime import datetime, timedelta
from .auth_db_operations import get_auth_record, insert_auth_record, update_auth_record, delete_auth_record

def validate_auth_id(auth_id):
    auth_record = get_auth_record(auth_id)

    if not auth_record:
        return False
    if auth_record.expires_at.timestamp() > datetime.now().timestamp():
        return True

    if refresh_token(auth_record):
        return True

    delete_auth_record(auth_id)
    return False

def exchange_code_for_token(code, state):
    token_url = "https://api.intra.42.fr/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
        'code': code,
        # 'state': state,
        'redirect_uri': settings.REDIRECT_URI,
    }
    response = requests.post(token_url, data=data)

    return response.json()

def refresh_token(auth_record):
    refresh_url = "https://api.intra.42.fr/oauth/token"
    data = {
        'grant_type': 'refresh_token',
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
        'refresh_token': auth_record.refresh_token,
    }
    response = requests.post(refresh_url, data=data)
    if response.status_code != 200:
        return False

    data = response.json()
    expires_at = datetime.fromtimestamp(data.get('created_at') + data.get('expires_in'))
    update_auth_record(auth_record.id, data.get('access_token'), data.get('refresh_token'), expires_at)

    return True

def get_user_info(access_token):
    user_info_url = "https://api.intra.42.fr/v2/me"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(user_info_url, headers=headers)
    return response.json()
