from ariadne import ObjectType, MutationType, make_executable_schema
import grpc
from main_service.protos.auth_pb2_grpc import AuthServiceStub
from main_service.protos.auth_pb2 import ExchangeCodeRequest
from main_service.protos.user_pb2_grpc import UserServiceStub
from main_service.protos.user_pb2 import CreateUserRequest
from main_service.protos.profile_pb2_grpc import ProfileServiceStub
from main_service.protos.profile_pb2 import CreateProfileRequest

type_defs = """
    type Mutation {
        exchangeCodeForToken(input: ExchangeCodeForTokenInput!): ExchangeCodeForTokenPayload!
    }

    input ExchangeCodeForTokenInput {
        code: String!
        state: String!
    }

    type ExchangeCodeForTokenPayload {
        jwtToken: String!
    }

    type Query {
        dummyField: String
    }
"""

GRPC_HOST = "auth_service"
GRPC_PORT = "50051"
GRPC_TARGET = f"{GRPC_HOST}:{GRPC_PORT}"

mutation = MutationType()

@mutation.field("exchangeCodeForToken")
def resolve_exchange_code_for_token(_, info, input):
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            stub = AuthServiceStub(channel)
            request = ExchangeCodeRequest(code=input["code"], state=input["state"])
            response = stub.ExchangeCodeForToken(request)

            # Create user
            with grpc.insecure_channel("user_service:50051") as channel:
                stub = UserServiceStub(channel)
                grpc_request = CreateUserRequest(
                    id=response.user_id, name=response.full_name, mail=response.mail
                )
                stub.CreateUser(grpc_request)

            try:
                # Create user profile
                with grpc.insecure_channel("user_service:50051") as channel:
                    stub = ProfileServiceStub(channel)
                    grpc_request = CreateProfileRequest(
                        user_id=response.user_id,
                        avatar_url=response.avatar_url,
                        nickname=response.name
                    )
                    stub.CreateProfile(grpc_request, timeout=5)
            except Exception as e:
                pass

        return {"jwtToken": response.jwt_token}
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")
    except Exception as ex:
        raise Exception(f"Error occurred while exchanging code for token: {str(ex)}")

query = ObjectType("Query")

schemaAuth = make_executable_schema(type_defs, query, mutation)
