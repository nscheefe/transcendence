import grpc
import json
from django.core.exceptions import ObjectDoesNotExist
from user_service.protos import settings_pb2_grpc, settings_pb2
from user.models import Setting


class SettingServiceHandler(settings_pb2_grpc.SettingServiceServicer):
    def __init__(self):
        pass

    def CreateSetting(self, request, context):
        """
        Create a new Setting or update an existing one with the same name and user_id.
        """
        try:
            # Update if a record with the same name and user_id exists; otherwise, create.
            setting, created = Setting.objects.update_or_create(
                name=request.name,
                user_id=request.user_id,
                defaults={'data': json.dumps(request.data)},  # Serialize JSON data
            )

            # Return the newly created or updated setting
            return settings_pb2.Setting(
                id=setting.id,
                name=setting.name,
                data=setting.data,  # Return the stored data as-is
                user_id=setting.user_id,
            )

        except Exception as e:
            # Catch unexpected errors and return an INTERNAL error
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to create or update setting: {str(e)}")
            return settings_pb2.Setting()

    def UpdateSetting(self, request, context):
        """
        Update a Setting by its ID.
        """
        try:
            # Fetch the setting object by its ID
            setting = Setting.objects.get(id=request.id)

            # Update the setting fields based on the request
            if request.name:
                setting.name = request.name
            if request.data:
                setting.data = json.dumps(request.data)  # Serialize JSON data
            if request.HasField("user_id"):  # Optional: Only update if user_id is provided
                setting.user_id = request.user_id

            # Save the updated setting
            setting.save()

            # Return the updated setting
            return settings_pb2.Setting(
                id=setting.id,
                name=setting.name,
                data=setting.data,  # Return stored data as-is
                user_id=setting.user_id,
            )

        except Setting.DoesNotExist:
            # Handle the case where the setting does not exist
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Setting with the given ID does not exist")
            return settings_pb2.Setting()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to update setting: {str(e)}")
            return settings_pb2.Setting()

    def GetSettingById(self, request, context):
        """
        Retrieve a specific Setting by its ID.
        """
        try:
            # Fetch the setting object by ID
            setting = Setting.objects.get(id=request.id)

            # Return the Setting object
            return settings_pb2.Setting(
                id=setting.id,
                name=setting.name,
                data=setting.data,  # Data as stored (assumed to be JSON in this case)
                user_id=setting.user_id,
            )

        except ObjectDoesNotExist:
            # Setting with the requested ID does not exist
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Setting not found")
            return settings_pb2.Setting()
        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to retrieve setting: {str(e)}")
            return settings_pb2.Setting()

    def GetSettingsByUserId(self, request, context):
        """
        Retrieve all Settings for a specific user by their user_id.
        """
        try:
            # Fetch all settings for the given user_id
            settings = Setting.objects.filter(user_id=request.user_id)

            # Populate the response with the list of settings
            return settings_pb2.SettingsResponse(
                settings=[
                    settings_pb2.Setting(
                        id=setting.id,
                        name=setting.name,
                        data=setting.data,
                        user_id=setting.user_id,
                    )
                    for setting in settings
                ]
            )

        except Exception as e:
            # Handle unexpected errors
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to retrieve settings: {str(e)}")
            return settings_pb2.SettingsResponse()

    @classmethod
    def as_servicer(cls):
        """
        Servicer registration helper to simplify integration.
        """
        return cls()
