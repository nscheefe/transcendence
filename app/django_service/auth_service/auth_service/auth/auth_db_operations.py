from django.db import IntegrityError
from .models import Auth

def insert_auth_record(access_token, refresh_token, expires_at, user_id):
    try:
        auth_record = Auth.objects.create(access_token=access_token, refresh_token=refresh_token, expires_at=expires_at, user_id=user_id)
        return auth_record.id
    except IntegrityError as e:
        print(f"Error inserting auth record: {e}")
        return None

def get_auth_record(auth_id):
    return Auth.objects.get(id=auth_id)

def update_auth_record(auth_id, access_token, refresh_token, expires_at):
    auth_record = Auth.objects.get(id=auth_id)
    auth_record.access_token = access_token
    auth_record.refresh_token = refresh_token
    auth_record.expires_at = expires_at
    auth_record.save()

def delete_auth_record(auth_id):
    Auth.objects.filter(id=auth_id).delete()
