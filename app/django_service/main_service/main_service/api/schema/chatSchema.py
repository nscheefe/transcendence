import graphene
import grpc
from main_service.protos.chat_pb2_grpc import ChatServiceStub
from main_service.protos.chat_pb2 import GetChatRequest, CreateChatRequest

# Define the chat type
class ChatType(graphene.ObjectType):
    id = graphene.Int()

# Define the GraphQL query type
class Query(graphene.ObjectType):
    chat = graphene.Field(ChatType, id=graphene.Int(required=True))

    def resolve_chat(self, info, id):
        # Connect to gRPC chat service
        channel = grpc.insecure_channel('chat_service:50051')  # Docker container service name
        client = ChatServiceStub(channel)

        # Call the gRPC service
        request = GetChatRequest(id=id)
        response = client.GetChat(request)

        if response.id == 0:
            return None

        return ChatType(
            id=response.id
        )

# Define the CreateChat mutation
class CreateChat(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    chat = graphene.Field(ChatType)

    def mutate(self, info, id):
        # Connect to gRPC chat service
        channel = grpc.insecure_channel('chat_service:50051')  # Docker container service name
        client = ChatServiceStub(channel)

        # Call the gRPC service
        request = CreateChatRequest(id=id)
        response = client.CreateChat(request)

        return CreateChat(chat=ChatType(
            id=response.id
        ))

# Define the mutation type
class Mutation(graphene.ObjectType):
    create_chat = CreateChat.Field()

# Update the schema to include the query and mutation
schema = graphene.Schema(query=Query, mutation=Mutation)