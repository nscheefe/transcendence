import grpc
import json
from django.db import IntegrityError
from user_service.protos import profile_pb2_grpc, profile_pb2
from user.models import Profile

class ProfileServiceHandler(profile_pb2_grpc.ProfileServiceServicer):
    def __init__(self):
        pass

    def GetProfile(self, request, context):
        try:
            profile = Profile.objects.get(user_id=request.user_id)
            return profile_pb2.Profile(
                user_id=profile.user.id,
                avatar_url=profile.avatar_url,
                nickname=profile.nickname,
                bio=profile.bio,
                additional_info=json.loads(profile.additional_info)  # Use get_additional_info if needed
            )
        except Profile.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Profile not found')
            return profile_pb2.Profile()

    def CreateOrUpdateProfile(self, request, context):
        profile, created = Profile.objects.update_or_create(
            user_id=request.user_id,
            defaults={
                'avatar_url': request.avatar_url,
                'nickname': request.nickname,
                'bio': request.bio,
                'additional_info': json.dumps(request.additional_info)  # Use set_additional_info if needed
            }
        )
        return profile_pb2.Profile(
            user_id=profile.user.id,
            avatar_url=profile.avatar_url,
            nickname=profile.nickname,
            bio=profile.bio,
            additional_info=json.loads(profile.additional_info)  # Use get_additional_info if needed
        )

    def DeleteProfile(self, request, context):
        try:
            profile = Profile.objects.get(user_id=request.user_id)
            profile.delete()
            return profile_pb2.ProfileDeleteResponse(
                success=True
            )
        except Profile.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Profile not found')
            return profile_pb2.ProfileDeleteResponse(
                success=False,
                message='Profile not found'
            )

    @classmethod
    def as_servicer(cls):
        return cls()

