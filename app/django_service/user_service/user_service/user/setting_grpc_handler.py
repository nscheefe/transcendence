import grpc
import json
from django.core.exceptions import ObjectDoesNotExist
from user_service.protos import settings_pb2_grpc, settings_pb2
from user.models import Setting

class SettingServiceHandler(settings_pb2_grpc.SettingServiceServicer):
    def __init__(self):
        pass

    def GetSetting(self, request, context):
        try:
            setting = Setting.objects.get(name=request.name, user_id=request.user_id)
            return settings_pb2.Setting(
                name=setting.name,
                data=setting.get_data(),  # Utilize the get_data method to return the JSON data
                user_id=setting.user.id
            )
        except Setting.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Setting not found')
            return settings_pb2.Setting()

    def CreateOrUpdateSetting(self, request, context):
        setting, created = Setting.objects.update_or_create(
            name=request.name,
            user_id=request.user_id,
            defaults={'data': json.dumps(request.data)}  # Serialize the data before saving
        )
        return settings_pb2.Setting(
            name=setting.name,
            data=setting.get_data(),  # Utilize the get_data method to return the JSON data
            user_id=setting.user.id
        )

    @classmethod
    def as_servicer(cls):
        return cls()

