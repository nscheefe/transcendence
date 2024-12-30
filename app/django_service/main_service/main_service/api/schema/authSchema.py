import graphene
import grpc
from main_service.protos.auth_pb2_grpc import AuthServiceStub
from main_service.protos.auth_pb2 import ExchangeCodeRequest, Empty
from main_service.protos.user_pb2_grpc import UserServiceStub
from main_service.protos.user_pb2 import CreateUserRequest

GRPC_HOST = "auth_service"
GRPC_PORT = "50051"
GRPC_TARGET = f"{GRPC_HOST}:{GRPC_PORT}"

class Query(graphene.ObjectType):
    redirect_uri = graphene.String(required=True)

    def resolve_redirect_uri(self, info):
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            stub = AuthServiceStub(channel)
            request = Empty()
            response = stub.GetRedirectUri(request)
            return response.redirect_uri

class ExchangeCodeForTokenInput(graphene.InputObjectType):
    code = graphene.String(required=True)
    state = graphene.String(required=True)

class ExchangeCodeForTokenMutation(graphene.Mutation):
    class Arguments:
        input = ExchangeCodeForTokenInput(required=True)

    jwt_token = graphene.String(required=True)

    def mutate(self, info, input=None):
        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                stub = AuthServiceStub(channel)
                request = ExchangeCodeRequest(code=input.code, state=input.state)
                response = stub.ExchangeCodeForToken(request)

                # Create user
                with grpc.insecure_channel("user_service:50051") as channel:
                    stub = UserServiceStub(channel)
                    grpc_request = CreateUserRequest(
                        id= response.user_id,
                        name=response.name,
                        mail=response.mail
                    )
                    stub.CreateUser(grpc_request)

            return ExchangeCodeForTokenMutation(
                jwt_token=response.jwt_token
            )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as ex:
            raise Exception(f"Error occurred while creating user: {str(ex)}")

class Mutation(graphene.ObjectType):
    exchange_code_for_token = ExchangeCodeForTokenMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)