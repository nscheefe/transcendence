import grpc
from concurrent import futures
from admin_service.protos import admin_pb2_grpc, admin_pb2
from admin_service.admin.models import Admin

class AdminServiceHandler(admin_pb2_grpc.AdminServiceServicer):
    def __init__(self):
        pass

    def GetAdmin(self, request, context):
        try:
            admin = Admin.objects.get(id=request.id)
            return admin_pb2.Admin(
                id=admin.id
            )
        except Admin.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Admin not found')
            return admin_pb2.Admin()

    def CreateAdmin(self, request, context):
        admin = Admin(
            id=request.id
        )
        admin.save()
        return admin_pb2.Admin(
            id=admin.id
        )

    def GetAdmins(self, request, context):
        admins = Admin.objects.all()
        return admin_pb2.AdminList(
            admins=[admin_pb2.Admin(id=admin.id) for admin in admins]
        )

    @classmethod
    def as_servicer(cls):
        return cls()

def grpc_handlers(server):
    admin_service_handler = AdminServiceHandler.as_servicer()
    admin_pb2_grpc.add_AdminServiceServicer_to_server(admin_service_handler, server)