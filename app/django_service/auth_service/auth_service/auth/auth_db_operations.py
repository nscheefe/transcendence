from django.db import IntegrityError
from .models import Auth

def insert_auth_record(token, user_id):
    try:
        auth_record = Auth.objects.create(token=token, user_id=user_id)
        return auth_record.id
    except IntegrityError as e:
        print(f"Error inserting auth record: {e}")
        return None

def get_token(user_id):
    return Auth.objects.get(user_id=user_id).token

def auth_id_exists(auth_id):
    return Auth.objects.filter(id=auth_id).exists()
