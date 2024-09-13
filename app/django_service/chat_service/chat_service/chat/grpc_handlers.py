import grpc
from concurrent import futures
from chat_service.protos import chat_pb2_grpc, chat_pb2
from chat_service.chat.models import Chat

class ChatServiceHandler(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        pass

    def GetChat(self, request, context):
        try:
            chat = Chat.objects.get(id=request.id)
            return chat_pb2.Chat(
                id=chat.id
            )
        except Chat.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Chat not found')
            return chat_pb2.Chat()

    def CreateChat(self, request, context):
        chat = Chat(
            id=request.id
        )
        chat.save()
        return chat_pb2.Chat(
            id=chat.id
        )

    def GetChats(self, request, context):
        chats = Chat.objects.all()
        return chat_pb2.ChatList(
            chats=[chat_pb2.Chat(id=chat.id) for chat in chats]
        )

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    chat_service_handler = ChatServiceHandler.as_servicer()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(chat_service_handler, server)