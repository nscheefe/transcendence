from django.db import IntegrityError
from .models import Auth, State

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


def insert_state_record(state):
    try:
        state_record = State.objects.create(state=state)
        return state_record
    except IntegrityError as e:
        print(f"Error inserting state record: {e}")
        return None

def check_and_delete_state(state):
    try:
        state_record = State.objects.get(state=state)
        state_record.delete()
        return True
    except State.DoesNotExist:
        return False