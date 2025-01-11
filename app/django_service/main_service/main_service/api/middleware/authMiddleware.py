import grpc
from django.http import JsonResponse
from main_service.protos.auth_pb2_grpc import AuthServiceStub
from main_service.protos.auth_pb2 import GetUserIDFromJwtTokenRequest, GetUserIDFromJwtTokenResponse

GRPC_HOST = "auth_service"
GRPC_PORT = "50051"
GRPC_TARGET = f"{GRPC_HOST}:{GRPC_PORT}"

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/auth/'):
            return self.get_response(request)

        jwt_token = request.COOKIES.get('jwt_token')

        if not jwt_token:
            return JsonResponse(
                {'error': 'No authentication cookie found'},
                status=401
            )

        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                stub = AuthServiceStub(channel)

                request_message = GetUserIDFromJwtTokenRequest(
                    jwt_token=jwt_token
                )

                response = stub.GetUserIDFromJwtToken(request_message)

                request.user_id = response.user_id
        except grpc.RpcError as e:
            return JsonResponse(
                {'error': 'Authentication failed', 'details': str(e)},
                status=401
            )
        except Exception as e:
            return JsonResponse(
                {'error': 'Internal server error', 'details': str(e)},
                status=500
            )

        return self.get_response(request)
