import grpc
from concurrent import futures
from auth_service.protos import auth_pb2_grpc, auth_pb2
from auth_service.auth.models import Auth
from django.conf import settings
import jwt
import requests
from auth_service.utils import generate_random_string
from auth_service.auth.auth_db_operations import *

class AuthServiceHandler(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        pass

    def GetRedirectUri(self, request, context):
        code = generate_random_string()
        insert_code_record(code)
        
        redirect_uri = f"https://api.intra.42.fr/oauth/authorize?client_id={settings.CLIENT_ID}&redirect_uri={settings.REDIRECT_URI}&state={code}&response_type=code"
        return auth_pb2.RedirectUriResponse(redirect_uri=redirect_uri)

    def ExchangeCodeForToken(self, request, context):
        if not check_and_delete_code(request.code):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid state code')
            return auth_pb2.TokenResponse()

        token_url = "https://api.intra.42.fr/oauth/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'code': request.code,
            'redirect_uri': settings.REDIRECT_URI,
        }
        response = requests.post(token_url, data=data)
        token_data = response.json()

        access_token = token_data.get('access_token')
        if not access_token:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid authorization code')
            return auth_pb2.TokenResponse()

        jwt_token = jwt.encode({'access_token': access_token}, settings.JWT_SECRET, algorithm='HS256')

        return auth_pb2.TokenResponse(jwt_token=jwt_token)

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    auth_service_handler = AuthServiceHandler.as_servicer()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(auth_service_handler, server)