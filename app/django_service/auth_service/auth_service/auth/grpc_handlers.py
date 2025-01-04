import grpc
from auth_service.protos import auth_pb2_grpc, auth_pb2
from django.conf import settings
import jwt
from auth_service.auth.auth_db_operations import *
from auth_service.auth.intra_api import *
from datetime import datetime

class AuthServiceHandler(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self):
        pass

    def ExchangeCodeForToken(self, request, context):
        token_data = exchange_code_for_token(request.code, request.state)
        if not token_data.get('access_token'):
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid authorization code')
            return auth_pb2.ExchangeCodeResponse()

        user_info = get_user_info(token_data.get('access_token'))
        if not user_info:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid access token')
            return auth_pb2.ExchangeCodeResponse()

        expires_at = datetime.fromtimestamp(token_data.get('created_at') + token_data.get('expires_in'))
        auth_id = insert_auth_record(token_data.get('access_token'), token_data.get('refresh_token'), expires_at, user_info.get('id'))

        jwt_token = jwt.encode({'auth_id': auth_id, 'user_id': user_info.get('id')}, settings.JWT_SECRET, algorithm='HS256')

        return auth_pb2.ExchangeCodeResponse(jwt_token=jwt_token, name=user_info.get('login'), mail=user_info.get('email'), user_id=user_info.get('id'), avatar_url=user_info.get('image')['link'], full_name=user_info.get('displayname'))
    
    def GetUserIDFromJwtToken(self, request, context):
        try:
            decoded_token = jwt.decode(request.jwt_token, settings.JWT_SECRET, algorithms=['HS256'])
            user_id = decoded_token['user_id']
            auth_id = decoded_token['auth_id']
        except jwt.ExpiredSignatureError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Token has expired')
            return auth_pb2.GetUserIDFromJwtTokenResponse()
        except jwt.InvalidTokenError:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid token')
            return auth_pb2.GetUserIDFromJwtTokenResponse()

        valid_auth = validate_auth_id(auth_id)
        if not valid_auth:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('No auth record found')
            return auth_pb2.GetUserIDFromJwtTokenResponse()

        return auth_pb2.GetUserIDFromJwtTokenResponse(user_id=user_id)

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    auth_service_handler = AuthServiceHandler.as_servicer()
    auth_pb2_grpc.add_AuthServiceServicer_to_server(auth_service_handler, server)