import graphene
import grpc
from main_service.protos.auth_pb2_grpc import AuthServiceStub
from main_service.protos.auth_pb2 import ExchangeCodeRequest
from main_service.protos.user_pb2_grpc import UserServiceStub
from main_service.protos.user_pb2 import CreateUserRequest
from main_service.protos.profile_pb2_grpc import ProfileServiceStub
from main_service.protos.profile_pb2 import CreateProfileRequest

GRPC_HOST = "auth_service"
GRPC_PORT = "50051"
GRPC_TARGET = f"{GRPC_HOST}:{GRPC_PORT}"

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
                
                try:
                    # Create user profile
                    with grpc.insecure_channel("user_service:50051") as channel:
                        stub = ProfileServiceStub(channel)
                        grpc_request = CreateProfileRequest(
                            user_id=response.user_id,
                            avatar_url=response.avatar_url,
                            nickname=response.full_name
                        )
                        stub.CreateProfile(grpc_request)
                except Exception as e:
                    pass

            return ExchangeCodeForTokenMutation(
                jwt_token=response.jwt_token
            )
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as ex:
            raise Exception(f"Error occurred while exchanging code for token: {str(ex)}")

# Add an empty Query root type
class Query(graphene.ObjectType):
    dummy_field = graphene.String()

# Add Mutation root type
class Mutation(graphene.ObjectType):
    exchange_code_for_token = ExchangeCodeForTokenMutation.Field()

# Create schema with both Query and Mutation root types
schemaAuth = graphene.Schema(query=Query, mutation=Mutation)
