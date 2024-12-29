import grpc
from concurrent import futures
from auth_service.protos import auth_pb2_grpc, auth_pb2
from auth_service.auth.models import Auth
from django.conf import settings
import jwt
import requests
from auth_service.utils import generate_random_string
from auth_service.auth.auth_db_operations import *
from auth_service.auth.intra_api import *
from datetime import datetime, timezone, timedelta

class AuthServiceHandler(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        pass

    def GetRedirectUri(self, request, context):
        code = generate_random_string()
        insert_code_record(code)
        
        redirect_uri = f"https://api.intra.42.fr/oauth/authorize?client_id={settings.CLIENT_ID}&redirect_uri={settings.REDIRECT_URI}&state={code}&response_type=code"
        return auth_pb2.RedirectUriResponse(redirect_uri=redirect_uri)

    def ExchangeCodeForToken(self, request, context):
        if not check_and_delete_code(request.state):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid state code')
            return auth_pb2.TokenResponse()

        token_data = exchange_code_for_token(request.code, request.state)
        access_token = token_data.get('access_token')
        if not access_token:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid authorization code')
            return auth_pb2.TokenResponse()
        
        user_info = get_user_info(access_token)
        # TODO: Create user with grpc via user_service
        insert_auth_record(access_token, user_info.get('id'))

        jwt_token = jwt.encode({'user_id': 1, 'exp': datetime.now(timezone.utc) + timedelta(seconds=7200)}, settings.JWT_SECRET, algorithm='HS256')

        return auth_pb2.TokenResponse(jwt_token=jwt_token)
    
    def GetUserIDFromJwtToken(self, request, context):
        try:
            decoded_token = jwt.decode(request.jwt_token, settings.JWT_SECRET, algorithms=['HS256'])
            user_id = decoded_token['user_id']
        except jwt.ExpiredSignatureError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Token has expired')
            return auth_pb2.GetUserIDFromJwtTokenResponse()
        except jwt.InvalidTokenError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid token')
            return auth_pb2.GetUserIDFromJwtTokenResponse()

        user_exists = user_exists(user_id)
        if not user_exists:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('User ID not found')
            return auth_pb2.GetUserIDFromJwtTokenResponse()

        return auth_pb2.GetUserIDFromJwtTokenResponse(user_id=str(user_id))

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    auth_service_handler = AuthServiceHandler.as_servicer()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(auth_service_handler, server)