from asyncio.log import logger
import logging
from math import log
from pydoc import resolve
#from tkinter import NO
from ariadne import ObjectType, MutationType, make_executable_schema, ScalarType
import grpc
from datetime import datetime

# Import the protobuf service stubs and request classes for each model
from main_service.protos.user_pb2_grpc import UserServiceStub
from main_service.protos.user_pb2 import GetUserRequest, CreateUserRequest
from main_service.protos.friendship_pb2_grpc import FriendshipServiceStub
from main_service.protos.friendship_pb2 import GetFriendshipsByUserIdRequest, CreateFriendshipRequest, UpdateFriendshipRequest, DeleteFriendshipRequest
from main_service.protos.notification_pb2_grpc import NotificationServiceStub
from main_service.protos.notification_pb2 import GetNotificationsByUserIdRequest, CreateNotificationRequest, DeleteNotificationRequest, UpdateNotificationRequest
from main_service.protos.permission_pb2_grpc import PermissionServiceStub
from main_service.protos.permission_pb2 import GetPermissionByIdRequest
from main_service.protos.profile_pb2_grpc import ProfileServiceStub
from main_service.protos.profile_pb2 import GetProfileByUserIdRequest, CreateProfileRequest, UpdateProfileRequest, GetAllProfilesRequest
from main_service.protos.role_pb2_grpc import RoleServiceStub
from main_service.protos.role_pb2 import GetRoleByIdRequest
from main_service.protos.rolePermission_pb2_grpc import RolePermissionServiceStub
from main_service.protos.rolePermission_pb2 import GetRolePermissionsByRoleIdRequest
from main_service.protos.settings_pb2_grpc import SettingServiceStub
from main_service.protos.settings_pb2 import GetSettingsByUserIdRequest, CreateSettingRequest, UpdateSettingRequest
from main_service.protos.userAchievement_pb2_grpc import UserAchievementServiceStub
from main_service.protos.userAchievement_pb2 import GetUserAchievementsByUserIdRequest, CreateUserAchievementRequest, UpdateUserAchievementRequest
from main_service.api.schema.objectTypes import query, mutation, subscription

GRPC_HOST = "user_service"
GRPC_PORT = "50051"
GRPC_TARGET = f"{GRPC_HOST}:{GRPC_PORT}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#query = ObjectType("Query")
#mutation = MutationType()

@query.field("user")
def resolve_user(_, info):
    logger.info("Fetching user")
    try:
        user_id = info.context["request"].user_id
        if not user_id:
            raise Exception("Authentication required: user_id is missing")

        channel = grpc.insecure_channel(GRPC_TARGET)
        client = UserServiceStub(channel)
        request = GetUserRequest(id=user_id)
        response = client.GetUser(request)
        return {
            "id": response.id,
            "name": response.name,
            "mail": response.mail,
            "blocked": response.blocked,
            "createdAt": datetime.fromtimestamp(response.created_at.seconds) if response.HasField("created_at") else None,
            "updatedAt": datetime.fromtimestamp(response.updated_at.seconds) if response.HasField("updated_at") else None,
            "roleId": response.role_id,
            "lastLogin": datetime.fromtimestamp(response.last_login.seconds) if response.HasField("last_login") else None,
            "lastLoginIp": response.last_login_ip
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return None
        else:
            raise e

user = ObjectType("User")

@user.field("profile")
def resolve_user_profile(obj, *_):
    logger.info(f"Fetching profile for user {obj['id']}")
    user_id = obj['id']
    try:
        channel = grpc.insecure_channel(GRPC_TARGET)
        client = ProfileServiceStub(channel)
        request = GetProfileByUserIdRequest(user_id=user_id)
        response = client.GetProfileByUserId(request)
        return {
            "id": response.id,
            "userId": response.user_id,
            "avatarUrl": response.avatar_url,
            "nickname": response.nickname,
            "bio": response.bio,
            "additionalInfo": response.additional_info,
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            logger.error(f"Profile not found for user {user_id}")
            return None
        else:
            raise e

@query.field("profile")
def resolve_profile(_, info, userId):
    logger.info(f"Fetching profile for user ID {userId}")
    try:
        userId = int(userId)
        if not userId:
            raise Exception("Authentication required: user_id is missing")

        channel = grpc.insecure_channel(GRPC_TARGET)
        client = ProfileServiceStub(channel)
        request = GetProfileByUserIdRequest(user_id=userId)
        response = client.GetProfileByUserId(request)
        return {
            "id": response.id,
            "userId": response.user_id,
            "avatarUrl": response.avatar_url,
            "nickname": response.nickname,
            "bio": response.bio,
            "additionalInfo": response.additional_info,
        }
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return None
        else:
            raise e

@query.field("getAllProfiles")
def resolve_get_all_profiles(_, info, limit, offset):
    del info
    try:
        with grpc.insecure_channel(GRPC_TARGET) as channel:
            stub = ProfileServiceStub(channel)
            grpc_request = GetAllProfilesRequest(limit=limit, offset=offset)
            grpc_response = stub.GetAllProfiles(grpc_request)

            profiles = [
                {
                    "id": profile.id,
                    "userId": profile.user_id,
                    "avatarUrl": profile.avatar_url,
                    "nickname": profile.nickname,
                    "bio": profile.bio,
                    "additionalInfo": profile.additional_info,
                }
                for profile in grpc_response.profiles
            ]

            return {
                "profiles": profiles,
                "totalCount": grpc_response.total_count,
            }

    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")
    except Exception as ex:
        raise Exception(f"Error occurred while fetching profiles: {str(ex)}")

@query.field("friendships")
def resolve_friendships(_, info):
    # Extract `user_id` from the request context (set via middleware)
    user_id = info.context["request"].user_id
    if not user_id:
        raise Exception("Authentication required: user_id is missing")  # Ensure the user is authenticated

    logger.info(f"Fetching friendships for user with ID: {user_id}")
    try:
        # Set up gRPC connection with the Friendship service
        channel = grpc.insecure_channel(GRPC_TARGET)
        client = FriendshipServiceStub(channel)

        # Make a GetFriendshipsByUserIdRequest via gRPC
        request = GetFriendshipsByUserIdRequest(user_id=user_id)
        response = client.GetFriendshipsByUserId(request)

        # Map the gRPC response to the expected GraphQL response format
        friendships = [
            {
                "userId": friendship.user_id,
                "friendId": friendship.friend_id,
                "establishedAt": datetime.fromtimestamp(friendship.established_at.seconds) if friendship.HasField(
                    "established_at") else None,
                "accepted": friendship.accepted,
            }
            for friendship in response.friendships
        ]

        return friendships  # Return the friendships list

    except grpc.RpcError as e:
        logger.error(f"Error fetching friendships for user {user_id}: {e.details()} (Code: {e.code()})")
        return []  # Return an empty list in case of error
    except Exception as e:
        logger.error(f"Unexpected error fetching friendships for user {user_id}: {str(e)}")
        return []  # Return an empty list for unexpected errors


@mutation.field("createUser")
def resolve_create_user(_, info, input):
    service_endpoint = GRPC_TARGET

    try:
        with grpc.insecure_channel(service_endpoint) as channel:
            stub = UserServiceStub(channel)
            grpc_request = CreateUserRequest(
                id=input.get("id"),
                name=input["name"],
                mail=input["mail"],
                blocked=input.get("blocked"),
                role_id=input.get("roleId"),
                last_login_ip=input.get("lastLoginIp", "")
            )
            grpc_response = stub.CreateUser(grpc_request)
            return {
                "id": grpc_response.id,
                "name": grpc_response.name,
                "mail": grpc_response.mail,
                "blocked": grpc_response.blocked,
                "roleId": grpc_response.role_id,
                "lastLoginIp": grpc_response.last_login_ip,
                "createdAt": datetime.fromtimestamp(grpc_response.created_at.seconds) if grpc_response.HasField("created_at") else None,
                "updatedAt": datetime.fromtimestamp(grpc_response.updated_at.seconds) if grpc_response.HasField("updated_at") else None,
            }
    except grpc.RpcError as e:
        raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")
    except Exception as ex:
        raise Exception(f"Error occurred while creating user: {str(ex)}")

@mutation.field("manageProfile")
def resolve_manage_profile(_, info, profileData):
    user_id = info.context["request"].user_id
    if not user_id:
        raise Exception("Authentication required: user_id is missing")
    logger.info("Manage profile data: " + str(profileData))
    try:
        channel = grpc.insecure_channel(GRPC_TARGET)
        profile_stub = ProfileServiceStub(channel)

        update_request = UpdateProfileRequest(
            user_id=user_id,
            avatar_url=profileData.get("avatarUrl"),
            nickname=profileData.get("nickname"),
            bio=profileData.get("bio"),
            additional_info=profileData.get("additionalInfo")
        )
        profile_stub.UpdateProfile(update_request)

        return {"success": True, "message": "Profile updated successfully."}

    except grpc.RpcError as e:
        return {"success": False, "message": f"gRPC Profile error: {e.details()} (Code: {e.code()})"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error during profile update: {str(e)}"}

@mutation.field("manageFriendship")
def resolve_manage_friendship(_, info, friendshipData):
    user_id = info.context["request"].user_id
    if not user_id:
        raise Exception("Authentication required: user_id is missing")

    try:
        channel = grpc.insecure_channel(GRPC_TARGET)
        friendship_stub = FriendshipServiceStub(channel)
        notification_stub = NotificationServiceStub(channel)

        if friendshipData.get("create"):
            create_request = CreateFriendshipRequest(
                user_id=user_id,
                friend_id=friendshipData["create"]["friendId"],
            )
            response = friendship_stub.CreateFriendship(create_request)
            if not response.id:
                raise Exception("Failed to create friendship.")
            notification_request = CreateNotificationRequest(
                user_id=friendshipData["create"]["friendId"],
                message=f"User {user_id} sent you a friend request.",
                read=False,
                sent_at=datetime.utcnow()
            )
            notification_stub.CreateNotification(notification_request)

        if friendshipData.get("update"):
            update_request = UpdateFriendshipRequest(
                user_id=user_id,
                friend_id=friendshipData["update"]["friendId"],
                accepted=friendshipData["update"]["accepted"],
            )
            friendship_stub.UpdateFriendship(update_request)

        if friendshipData.get("delete"):
            delete_request = DeleteFriendshipRequest(
                id=friendshipData["delete"]["id"]
            )
            delete_response = friendship_stub.DeleteFriendship(delete_request)
            if not delete_response.success:
                raise Exception("Failed to delete friendship.")

        return {"success": True, "message": "Friendship (and optionally notifications) completed successfully."}

    except grpc.RpcError as e:
        return {"success": False, "message": f"gRPC error: {e.details()} (Code: {e.code()})"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

@mutation.field("manageNotification")
def resolve_manage_notification(_, info, notificationData):
    user_id = info.context["request"].user_id
    if not user_id:
        raise Exception("Authentication required: user_id is missing")

    try:
        channel = grpc.insecure_channel(GRPC_TARGET)
        notification_stub = NotificationServiceStub(channel)

        if notificationData.get("create"):
            create_request = CreateNotificationRequest(
                user_id=user_id,
                message=notificationData["create"]["message"],
                read=notificationData["create"]["read"],
                sent_at=notificationData["create"]["sentAt"],
            )
            notification_stub.CreateNotification(create_request)

        if notificationData.get("update"):
            update_request = UpdateNotificationRequest(
                user_id=user_id,
                message=notificationData["update"]["message"],
                read=notificationData["update"]["read"],
            )
            notification_stub.UpdateNotification(update_request)

        if notificationData.get("delete"):
            delete_request = DeleteNotificationRequest(
                id=notificationData["delete"]["id"]
            )
            delete_response = notification_stub.DeleteNotification(delete_request)
            if not delete_response.success:
                raise Exception("Failed to delete notification.")

        return {"success": True, "message": "Notification operations completed successfully."}

    except grpc.RpcError as e:
        return {"success": False, "message": f"gRPC error: {e.details()} (Code: {e.code()})"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

@mutation.field("manageSetting")
def resolve_manage_setting(_, info, settingData):
    user_id = info.context["request"].user_id
    if not user_id:
        raise Exception("Authentication required: user_id is missing")

    try:
        channel = grpc.insecure_channel(GRPC_TARGET)
        setting_stub = SettingServiceStub(channel)

        if settingData.get("create"):
            create_request = CreateSettingRequest(
                user_id=user_id,
                name=settingData["create"]["name"],
                data=settingData["create"]["data"],
            )
            setting_stub.CreateSetting(create_request)

        if settingData.get("update"):
            update_request = UpdateSettingRequest(
                user_id=user_id,
                name=settingData["update"]["name"],
                data=settingData["update"]["data"],
            )
            setting_stub.UpdateSetting(update_request)

        return {"success": True, "message": "Setting operations completed successfully."}

    except grpc.RpcError as e:
        return {"success": False, "message": f"gRPC error: {e.details()} (Code: {e.code()})"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

@mutation.field("manageUserAchievement")
def resolve_manage_user_achievement(_, info, achievementData):
    user_id = info.context["request"].user_id
    if not user_id:
        raise Exception("Authentication required: user_id is missing")

    try:
        channel = grpc.insecure_channel(GRPC_TARGET)
        achievement_stub = UserAchievementServiceStub(channel)

        if achievementData.get("create"):
            create_request = CreateUserAchievementRequest(
                user_id=user_id,
                achievement_id=achievementData["create"]["achievementId"],
                unlocked_at=achievementData["create"]["unlockedAt"],
            )
            achievement_stub.CreateUserAchievement(create_request)

        if achievementData.get("update"):
            update_request = UpdateUserAchievementRequest(
                user_id=user_id,
                achievement_id=achievementData["update"]["achievementId"],
                unlocked_at=achievementData["update"]["unlockedAt"],
            )
            achievement_stub.UpdateUserAchievement(update_request)

        return {"success": True, "message": "User Achievement operations completed successfully."}

    except grpc.RpcError as e:
        return {"success": False, "message": f"gRPC error: {e.details()} (Code: {e.code()})"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

resolver = [query, mutation, subscription, user]
