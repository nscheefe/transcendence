import grpc
import json
from django.db import IntegrityError
from user_service.protos import profile_pb2_grpc, profile_pb2
from user.models import Profile


class ProfileServiceHandler(profile_pb2_grpc.ProfileServiceServicer):
    def __init__(self):
        pass

    # Fetch profile by profile ID
    def GetProfileById(self, request, context):
        try:
            profile = Profile.objects.get(id=request.id)
            return profile_pb2.Profile(
                id=profile.id,
                user_id=profile.user.id,
                avatar_url=profile.avatar_url,
                nickname=profile.nickname,
                bio=profile.bio,
                additional_info=json.dumps(profile.additional_info),
            )
        except Profile.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Profile not found')
            return profile_pb2.Profile()

    # Fetch profile by user ID
    def GetProfileByUserId(self, request, context):
        try:
            profile = Profile.objects.get(user_id=request.user_id)
            return profile_pb2.Profile(
                id=profile.id,
                user_id=profile.user.id,
                avatar_url=profile.avatar_url,
                nickname=profile.nickname,
                bio=profile.bio,
                additional_info=json.dumps(profile.additional_info),
            )
        except Profile.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Profile not found')
            return profile_pb2.Profile()

    # Create a new profile
    def CreateProfile(self, request, context):
        try:
            # Ensure no profile already exists for the user
            if Profile.objects.filter(user_id=request.user_id).exists():
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details("Profile already exists for this user ID")
                return profile_pb2.Profile()

            # Validate and parse additional_info
            if request.additional_info.strip():  # Ensure non-empty string
                try:
                    additional_info = json.loads(request.additional_info)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON in additional_info")
            else:
                additional_info = {}  # Default to empty dictionary

            # Create the profile
            profile = Profile.objects.create(
                user_id=request.user_id,
                avatar_url=request.avatar_url,
                nickname=request.nickname,
                bio=request.bio,
                additional_info=json.dumps(additional_info),
            )
            return profile_pb2.Profile(
                id=profile.id,
                user_id=profile.user.id,
                avatar_url=profile.avatar_url,
                nickname=profile.nickname,
                bio=profile.bio,
                additional_info=json.dumps(additional_info),
            )
        except ValueError as ve:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Failed to create profile: ' + str(ve))
            return profile_pb2.Profile()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failed to create profile: ' + str(e))
            return profile_pb2.Profile()

    # Update an existing profile
    def UpdateProfile(self, request, context):
        try:
            # Ensure the profile exists
            try:
                profile = Profile.objects.get(id=request.id)
            except Profile.DoesNotExist:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Profile not found')
                return profile_pb2.Profile()

            # Update the profile fields
            profile.avatar_url = request.avatar_url
            profile.nickname = request.nickname
            profile.bio = request.bio
            profile.additional_info = json.dumps(json.loads(request.additional_info))  # Handle JSON string
            profile.save()

            return profile_pb2.Profile(
                id=profile.id,
                user_id=profile.user.id,
                avatar_url=profile.avatar_url,
                nickname=profile.nickname,
                bio=profile.bio,
                additional_info=json.dumps(profile.additional_info),
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failed to update profile: ' + str(e))
            return profile_pb2.Profile()

    # Delete an existing profile by user ID
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
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failed to delete profile: ' + str(e))
            return profile_pb2.ProfileDeleteResponse(
                success=False,
                message=str(e)
            )

    # Fetch all profiles with pagination
    def GetAllProfiles(self, request, context):
        try:
            # Query profiles with requested limit and offset
            profiles_queryset = Profile.objects.all()[request.offset: request.offset + request.limit]
            total_count = Profile.objects.count()

            # Build response
            profiles = [
                profile_pb2.Profile(
                    id=profile.id,
                    user_id=profile.user.id,
                    avatar_url=profile.avatar_url,
                    nickname=profile.nickname,
                    bio=profile.bio,
                    additional_info=json.dumps(profile.additional_info),  # Serialize additional_info
                )
                for profile in profiles_queryset
            ]

            return profile_pb2.GetAllProfilesResponse(
                profiles=profiles,
                total_count=total_count
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Failed to fetch profiles: ' + str(e))
            return profile_pb2.GetAllProfilesResponse(
                profiles=[],  # Return an empty list in case of failure
                total_count=0
            )

    @classmethod
    def as_servicer(cls):
        # Setup to add this servicer to the gRPC server
        return cls()
