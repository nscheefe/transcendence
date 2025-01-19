import grpc
from django.http import JsonResponse
from main_service.protos.auth_pb2_grpc import AuthServiceStub
from main_service.protos.auth_pb2 import GetUserIDFromJwtTokenRequest

GRPC_HOST = "auth_service"
GRPC_PORT = "50051"
GRPC_TARGET = f"{GRPC_HOST}:{GRPC_PORT}"

class AuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, request, receive=None, send=None):
        if receive is None and send is None:
            # WSGI context
            if request.path.startswith('/auth/'):
                return self.inner(request)

            jwt_token = request.COOKIES.get('jwt_token')

            if not jwt_token:
                return JsonResponse(
                    {'error': 'No authentication cookie found'},
                    status=401
                )

            try:
                with grpc.insecure_channel(GRPC_TARGET) as channel:
                    stub = AuthServiceStub(channel)
                    request_message = GetUserIDFromJwtTokenRequest(jwt_token=jwt_token)
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

            return self.inner(request)
        else:
            # ASGI context
            return self.__call_async__(request, receive, send)

    async def __call_async__(self, scope, receive, send):
        if scope["type"] == "http":
            return await self.__call__(scope["asgi"]["http.request"])

        if scope["type"] == "websocket":
            jwt_token = None
            for header in scope["headers"]:
                if header[0] == b"cookie":
                    cookies = header[1].decode().split("; ")
                    for cookie in cookies:
                        if cookie.startswith("jwt_token="):
                            jwt_token = cookie.split("=")[1]
                            break

            if jwt_token:
                try:
                    async with grpc.aio.insecure_channel(GRPC_TARGET) as channel:
                        stub = AuthServiceStub(channel)
                        request_message = GetUserIDFromJwtTokenRequest(jwt_token=jwt_token)
                        response = await stub.GetUserIDFromJwtToken(request_message)
                        scope["user_id"] = response.user_id
                except grpc.RpcError as e:
                    print(f"Authentication failed: {e.details()}")
                except Exception as e:
                    print(f"Internal server error: {str(e)}")

            return await self.inner(scope, receive, send)

def AuthMiddlewareStack(inner):
    return AuthMiddleware(inner)
