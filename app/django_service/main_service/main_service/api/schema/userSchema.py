from datetime import datetime

import graphene
import grpc

# Import the protobuf service stubs and request classes for each model
from main_service.protos.user_pb2_grpc import UserServiceStub
from  main_service.protos.user_pb2 import GetUserRequest, CreateUserRequest
from main_service.protos.friendship_pb2_grpc import FriendshipServiceStub
from main_service.protos.friendship_pb2 import GetFriendshipByIdRequest, GetFriendshipsByUserIdRequest, CreateFriendshipRequest, UpdateFriendshipRequest, DeleteFriendshipRequest
from main_service.protos.notification_pb2_grpc import NotificationServiceStub
from main_service.protos.notification_pb2 import GetNotificationByIdRequest, GetNotificationsByUserIdRequest, CreateNotificationRequest, DeleteNotificationRequest, UpdateNotificationRequest
from main_service.protos.permission_pb2_grpc import PermissionServiceStub
from main_service.protos.permission_pb2 import GetPermissionByIdRequest
from main_service.protos.profile_pb2_grpc import ProfileServiceStub
from main_service.protos.profile_pb2 import GetProfileByIdRequest, GetProfileByUserIdRequest, CreateProfileRequest, UpdateProfileRequest, GetAllProfilesRequest
from main_service.protos.role_pb2_grpc import RoleServiceStub
from main_service.protos.role_pb2 import GetRoleByIdRequest
from main_service.protos.rolePermission_pb2_grpc import RolePermissionServiceStub
from main_service.protos.rolePermission_pb2 import GetRolePermissionsByRoleIdRequest
from main_service.protos.settings_pb2_grpc import SettingServiceStub
from main_service.protos.settings_pb2 import GetSettingsByUserIdRequest, CreateSettingRequest, UpdateSettingRequest
from main_service.protos.userAchievement_pb2_grpc import UserAchievementServiceStub
from main_service.protos.userAchievement_pb2 import GetUserAchievementsByUserIdRequest, CreateUserAchievementRequest, UpdateUserAchievementRequest

GRPC_HOST = "user_service"
GRPC_PORT = "50051"
GRPC_TARGET = f"{GRPC_HOST}:{GRPC_PORT}"

class UserType(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    mail = graphene.String()
    blocked = graphene.Boolean()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    role_id = graphene.Int()
    last_login = graphene.DateTime()
    last_login_ip = graphene.String()

class FriendshipType(graphene.ObjectType):
    user_id = graphene.Int()
    friend_id = graphene.Int()
    established_at = graphene.DateTime()
    accepted = graphene.Boolean()

class NotificationType(graphene.ObjectType):
    user_id = graphene.Int()
    message = graphene.String()
    read = graphene.Boolean()
    sent_at = graphene.DateTime()

class PermissionType(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()

class ProfileType(graphene.ObjectType):
    user_id = graphene.Int()
    avatar_url = graphene.String()
    nickname = graphene.String()
    bio = graphene.String()
    additional_info = graphene.String()

class GetAllProfilesResponseType(graphene.ObjectType):
    profiles = graphene.List(ProfileType)
    total_count = graphene.Int()

class RoleType(graphene.ObjectType):
    name = graphene.String()
    role_permissions = graphene.List(lambda: RolePermissionType)  # Nested Role Permissions
    def resolve_role_permissions(self, info):
        """Resolver fetching RolePermission details for the Role"""
        channel = grpc.insecure_channel(GRPC_TARGET)
        client = RolePermissionServiceStub(channel)
        request = GetRolePermissionsByRoleIdRequest(role_id=self.id)
        response = client.GetRolePermissionsByRoleId(request)

        return [
            RolePermissionType(
                role_id=record.role_id,
                permission_id=record.permission_id
            )
            for record in response.role_permissions
        ]


class RolePermissionType(graphene.ObjectType):
    role_id = graphene.Int()
    permission_id = graphene.Int()
    permission = graphene.Field(lambda: PermissionType)  # Nested PermissionType
    def resolve_permission(self, info):
        """Resolver for nested Permission inside RolePermissionType"""
        channel = grpc.insecure_channel(GRPC_TARGET)
        client = PermissionServiceStub(channel)
        request = GetPermissionByIdRequest(id=self.permission_id)
        response = client.GetPermissionById(request)

        return PermissionType(
            name=response.name,
            description=response.description
        )


class SettingType(graphene.ObjectType):
    user_id = graphene.Int()
    name = graphene.String()
    data = graphene.String()

class UserAchievementType(graphene.ObjectType):
    user_id = graphene.Int()
    achievement_id = graphene.Int()
    unlocked_at = graphene.DateTime()

class UserType(graphene.ObjectType):
        id = graphene.Int()
        name = graphene.String()
        mail = graphene.String()
        blocked = graphene.Boolean()
        created_at = graphene.DateTime()
        updated_at = graphene.DateTime()
        role_id = graphene.Int()
        last_login = graphene.DateTime()
        last_login_ip = graphene.String()

        # Nested types
        profile = graphene.Field(lambda: ProfileType)  # User's Profile
        friendships = graphene.List(lambda: FriendshipType)  # User's Friendships
        notifications = graphene.List(lambda: NotificationType)  # User's Notifications
        settings = graphene.List(lambda: SettingType)  # User's Settings
        achievements = graphene.List(lambda: UserAchievementType)  # User's Achievements
        role = graphene.Field(lambda: RoleType)  # User's Role (with permissions)

        ### Resolvers ###
        def resolve_profile(self, info):
            """Fetch the user's profile."""
            try:
                channel = grpc.insecure_channel(GRPC_TARGET)
                client = ProfileServiceStub(channel)
                request = GetProfileByUserIdRequest(user_id=self.id)
                response = client.GetProfileByUserId(request)

                return ProfileType(
                    user_id=response.user_id,
                    avatar_url=response.avatar_url,
                    nickname=response.nickname,
                    bio=response.bio,
                    additional_info=response.additional_info,
                )

            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    # Return None or raise a custom GraphQL error
                    return None
                else:
                    # Raise other unexpected errors as-is
                    raise e

        def resolve_friendships(self, info):
            """Fetch friendships for the user."""
            channel = grpc.insecure_channel(GRPC_TARGET)
            client = FriendshipServiceStub(channel)
            request = GetFriendshipsByUserIdRequest(user_id=self.id)
            response = client.GetFriendshipsByUserId(request)

            return [
                FriendshipType(
                    user_id=record.user_id,
                    friend_id=record.friend_id,
                    established_at=datetime.fromtimestamp(record.established_at.seconds),
                    accepted=record.accepted
                )
                for record in response.friendships
            ]

        def resolve_notifications(self, info):
            """Fetch notifications for the user."""
            channel = grpc.insecure_channel(GRPC_TARGET)
            client = NotificationServiceStub(channel)
            request = GetNotificationsByUserIdRequest(user_id=self.id)
            response = client.GetNotificationsByUserId(request)

            return [
                NotificationType(
                    user_id=record.user_id,
                    message=record.message,
                    read=record.read,
                    sent_at=datetime.fromtimestamp(record.sent_at.seconds),
                )
                for record in response.notifications
            ]

        def resolve_settings(self, info):
            """Fetch settings for the user."""
            channel = grpc.insecure_channel(GRPC_TARGET)
            client = SettingServiceStub(channel)
            request = GetSettingsByUserIdRequest(user_id=self.id)
            response = client.GetSettingsByUserId(request)

            return [
                SettingType(
                    user_id=record.user_id,
                    name=record.name,
                    data=record.data
                )
                for record in response.settings
            ]

        def resolve_achievements(self, info):
            """Fetch achievements for the user."""
            channel = grpc.insecure_channel(GRPC_TARGET)
            client = UserAchievementServiceStub(channel)

            # gRPC request
            request = GetUserAchievementsByUserIdRequest(user_id=self.id)
            response = client.GetUserAchievementsByUserId(request)

            # Check if achievements exist, otherwise return an empty list
            if not response.userAchievements:
                return []  # Explicitly return an empty list if no achievements exist

            # Map achievements to the required type
            return [
                UserAchievementType(
                    user_id=record.user_id,
                    achievement_id=record.achievement_id,
                    unlocked_at=datetime.fromtimestamp(record.unlocked_at.seconds)
                )
                for record in response.userAchievements
            ]

        def resolve_role(self, info):
            """Fetch the user's role."""
            channel = grpc.insecure_channel(GRPC_TARGET)
            client = RoleServiceStub(channel)
            request = GetRoleByIdRequest(id=self.role_id)
            response = client.GetRoleById(request)

            return RoleType(
                name=response.name,
            )


# Define the GraphQL query type
class Query(graphene.ObjectType):
    user = graphene.Field(UserType)
    profile = graphene.Field(ProfileType, user_id=graphene.Int(required=True))

    def resolve_user(self, info):
        user_id = info.context.user_id
        if not user_id:
            raise Exception("Authentication required: user_id is missing")

        channel = grpc.insecure_channel(GRPC_TARGET)
        client = UserServiceStub(channel)
        request = GetUserRequest(id=user_id)
        response = client.GetUser(request)
        return UserType(
            id=response.id,
            name=response.name,
            mail=response.mail,
            blocked=response.blocked,
            created_at=datetime.fromtimestamp(response.created_at.seconds),
            updated_at=datetime.fromtimestamp(response.updated_at.seconds),
            role_id=response.role_id,
            last_login=datetime.fromtimestamp(response.last_login.seconds),
            last_login_ip=response.last_login_ip
        )

    get_all_profiles = graphene.Field(
        GetAllProfilesResponseType,
        limit=graphene.Int(required=True),
        offset=graphene.Int(required=True),
    )

    @staticmethod
    def resolve_get_all_profiles(self, info, limit, offset):

        service_endpoint = GRPC_TARGET

        try:
            with grpc.insecure_channel(service_endpoint) as channel:
                # Create gRPC stub
                stub = ProfileServiceStub(channel)

                # Prepare the request
                grpc_request = GetAllProfilesRequest(
                    limit=limit,
                    offset=offset,
                )

                # Call the gRPC method
                grpc_response = stub.GetAllProfiles(grpc_request)

                profiles = [
                    ProfileType(
                        user_id=profile.user_id,
                        avatar_url=profile.avatar_url,
                        nickname=profile.nickname,
                        bio=profile.bio,
                        additional_info=profile.additional_info,
                    )
                    for profile in grpc_response.profiles
                ]

                return GetAllProfilesResponseType(
                    profiles=profiles,
                    total_count=grpc_response.total_count,
                )

        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as ex:
            raise Exception(f"Error occurred while fetching profiles: {str(ex)}")

    @staticmethod
    def resolve_profile(self, info, user_id:int):
        """Fetch the user's profile."""
        try:
            channel = grpc.insecure_channel(GRPC_TARGET)
            client = ProfileServiceStub(channel)
            request = GetProfileByUserIdRequest(user_id=user_id)
            response = client.GetProfileByUserId(request)

            return ProfileType(
                user_id=response.user_id,
                avatar_url=response.avatar_url,
                nickname=response.nickname,
                bio=response.bio,
                additional_info=response.additional_info,
            )

        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                # Return None or raise a custom GraphQL error
                return None
            else:
                # Raise other unexpected errors as-is
                raise e

##############################################################################################


class FriendshipFields(graphene.InputObjectType):
    friend_id = graphene.Int()
    established_at = graphene.DateTime()
    accepted = graphene.Boolean()


class FriendshipDeleteInput(graphene.InputObjectType):
    id = graphene.Int(required=True)


class FriendshipInput(graphene.InputObjectType):
    create = graphene.Field(FriendshipFields)
    update = graphene.Field(FriendshipFields)
    delete = graphene.Field(FriendshipDeleteInput)

class FriendshipMutation(graphene.Mutation):
    class Arguments:
        friendship_data = FriendshipInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, friendship_data):
        user_id = info.context.user_id

        if not user_id:
            raise Exception("Authentication required: user_id is missing")

        try:
            channel = grpc.insecure_channel(GRPC_TARGET)
            friendship_stub = FriendshipServiceStub(channel)
            notification_stub = NotificationServiceStub(channel)

            if friendship_data.create:
                create_request = CreateFriendshipRequest(
                    user_id=user_id,
                    friend_id=friendship_data.create.friend_id,
                    established_at=friendship_data.create.established_at,
                    accepted=friendship_data.create.accepted,
                )

                response = friendship_stub.CreateFriendship(create_request)

                if not response.id:
                    raise Exception("Failed to create friendship.")
                notification_request = CreateNotificationRequest(
                    user_id=friendship_data.create.friend_id,
                    message=f"User {user_id} sent you a friend request.",
                    read=False,
                    sent_at=datetime.utcnow()
                )
                notification_stub.CreateNotification(notification_request)
            if friendship_data.update:
                update_request = UpdateFriendshipRequest(
                    user_id=user_id,
                    friend_id=friendship_data.update.friend_id,
                    accepted=friendship_data.update.accepted,
                )
                friendship_stub.UpdateFriendship(update_request)
            if friendship_data.delete:
                delete_request = DeleteFriendshipRequest(
                    id=friendship_data.delete.id
                )
                delete_response = friendship_stub.DeleteFriendship(delete_request)

                if not delete_response.success:
                    raise Exception("Failed to delete friendship.")

            return FriendshipMutation(
                success=True, message="Friendship (and optionally notifications) completed successfully."
            )

        except grpc.RpcError as e:
            return FriendshipMutation(success=False, message=f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as e:
            return FriendshipMutation(success=False, message=f"Unexpected error: {str(e)}")


########################################################################################################################
class NotificationFields(graphene.InputObjectType):
    message = graphene.String()
    read = graphene.Boolean()
    sent_at = graphene.DateTime()


class NotificationDeleteInput(graphene.InputObjectType):
    id = graphene.Int(required=True)

class NotificationInput(graphene.InputObjectType):
    create = graphene.Field(NotificationFields)
    update = graphene.Field(NotificationFields)
    delete = graphene.Field(NotificationDeleteInput)

class NotificationMutation(graphene.Mutation):
    class Arguments:
        notification_data = NotificationInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, notification_data):
        user_id = info.context.user_id

        if not user_id:
            raise Exception("Authentication required: user_id is missing")

        try:
            channel = grpc.insecure_channel(GRPC_TARGET)
            notification_stub = NotificationServiceStub(channel)

            if notification_data.create:
                create_request = CreateNotificationRequest(
                    user_id=user_id,
                    message=notification_data.create.message,
                    read=notification_data.create.read,
                    sent_at=notification_data.create.sent_at,
                )
                notification_stub.CreateNotification(create_request)
            if notification_data.update:
                update_request = UpdateNotificationRequest(
                    user_id=user_id,
                    message=notification_data.update.message,
                    read=notification_data.update.read,
                )
                notification_stub.UpdateNotification(update_request)
            if notification_data.delete:
                delete_request = DeleteNotificationRequest(
                    id=notification_data.delete.id
                )
                delete_response = notification_stub.DeleteNotification(delete_request)

                if not delete_response.success:
                    raise Exception("Failed to delete notification.")

            return NotificationMutation(
                success=True, message="Notification operations completed successfully."
            )

        except grpc.RpcError as e:
            return NotificationMutation(success=False, message=f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as e:
            return NotificationMutation(success=False, message=f"Unexpected error: {str(e)}")

########################################################################################################################

class SettingFields(graphene.InputObjectType):
    name = graphene.String()
    data = graphene.String()


class SettingInput(graphene.InputObjectType):
    create = graphene.Field(SettingFields)
    update = graphene.Field(SettingFields)
class SettingMutation(graphene.Mutation):
    class Arguments:
        setting_data = SettingInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, setting_data):
        user_id = info.context.user_id

        if not user_id:
            raise Exception("Authentication required: user_id is missing")

        try:
            channel = grpc.insecure_channel(GRPC_TARGET)
            setting_stub = SettingServiceStub(channel)

            if setting_data.create:
                create_request = CreateSettingRequest(
                    user_id=user_id,
                    name=setting_data.create.name,
                    data=setting_data.create.data,
                )
                setting_stub.CreateSetting(create_request)

            # Handle Update Setting
            if setting_data.update:
                update_request = UpdateSettingRequest(
                    user_id=user_id,
                    name=setting_data.update.name,
                    data=setting_data.update.data,
                )
                setting_stub.UpdateSetting(update_request)

            return SettingMutation(success=True, message="Setting operations completed successfully.")

        except grpc.RpcError as e:
            return SettingMutation(success=False, message=f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as e:
            return SettingMutation(success=False, message=f"Unexpected error: {str(e)}")

########################################################################################################################

class UserAchievementFields(graphene.InputObjectType):
    achievement_id = graphene.Int()
    unlocked_at = graphene.DateTime()


class UserAchievementInput(graphene.InputObjectType):
    create = graphene.Field(UserAchievementFields)
    update = graphene.Field(UserAchievementFields)

class UserAchievementMutation(graphene.Mutation):
    class Arguments:
        achievement_data = UserAchievementInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, achievement_data):
        user_id = info.context.user_id

        if not user_id:
            raise Exception("Authentication required: user_id is missing")

        try:
            channel = grpc.insecure_channel(GRPC_TARGET)
            achievement_stub = UserAchievementServiceStub(channel)
            if achievement_data.create:
                create_request = CreateUserAchievementRequest(
                    user_id=user_id,
                    achievement_id=achievement_data.create.achievement_id,
                    unlocked_at=achievement_data.create.unlocked_at,
                )
                achievement_stub.CreateUserAchievement(create_request)
            if achievement_data.update:
                update_request = UpdateUserAchievementRequest(
                    user_id=user_id,
                    achievement_id=achievement_data.update.achievement_id,
                    unlocked_at=achievement_data.update.unlocked_at,
                )
                achievement_stub.UpdateUserAchievement(update_request)

            return UserAchievementMutation(success=True, message="User Achievement operations completed successfully.")

        except grpc.RpcError as e:
            return UserAchievementMutation(success=False, message=f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as e:
            return UserAchievementMutation(success=False, message=f"Unexpected error: {str(e)}")


########################################################################################################################

class ProfileFields(graphene.InputObjectType):
    avatar_url = graphene.String()
    nickname = graphene.String()
    bio = graphene.String()
    additional_info = graphene.String()


class ProfileInput(graphene.InputObjectType):
    create = graphene.Field(ProfileFields)
    update = graphene.Field(ProfileFields)


class ProfileMutation(graphene.Mutation):
    class Arguments:
        profile_data = ProfileInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, profile_data):
        user_id = info.context.user_id

        if not user_id:
            raise Exception("Authentication required: user_id is missing")
        try:
            channel = grpc.insecure_channel(GRPC_TARGET)
            profile_stub = ProfileServiceStub(channel)
            if profile_data.create:
                create_request = CreateProfileRequest(
                    user_id=user_id,
                    avatar_url=profile_data.create.avatar_url,
                    nickname=profile_data.create.nickname,
                    bio=profile_data.create.bio,
                    additional_info=profile_data.create.additional_info
                )
                profile_stub.CreateProfile(create_request)

            if profile_data.update:
                update_request = UpdateProfileRequest(
                    user_id=user_id,
                    avatar_url=profile_data.update.avatar_url,
                    nickname=profile_data.update.nickname,
                    bio=profile_data.update.bio,
                    additional_info=profile_data.update.additional_info
                )
                profile_stub.UpdateProfile(update_request)
            return ProfileMutation(success=True, message="Profile operations completed successfully.")

        except grpc.RpcError as e:
            return ProfileMutation(success=False, message=f"gRPC Profile error: {e.details()} (Code: {e.code()})")
        except Exception as e:
            return ProfileMutation(success=False, message=f"Unexpected error during profile operations: {str(e)}")

########################################################################################################################
class UserInput(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String(required=True)
    mail = graphene.String(required=True)
    blocked = graphene.Boolean()
    created_at = graphene.DateTime()
    updated_at = graphene.DateTime()
    role_id = graphene.Int()
    last_login = graphene.DateTime()
    last_login_ip = graphene.String()




class CreateUser(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    user = graphene.Field(UserType)

    @staticmethod
    def mutate(root, info, input=None):
        service_endpoint = GRPC_TARGET

        try:
            with grpc.insecure_channel(service_endpoint) as channel:
                stub = UserServiceStub(channel)
                grpc_request = CreateUserRequest(
                    id= input.id,
                    name=input.name,
                    mail=input.mail,
                    blocked=input.blocked,
                    role_id=input.role_id,
                    last_login_ip=input.last_login_ip or ""
                )
                grpc_response = stub.CreateUser(grpc_request)
                user_data = UserType(
                    id=grpc_response.id,
                    name=grpc_response.name,
                    mail=grpc_response.mail,
                    blocked=grpc_response.blocked,
                    role_id=grpc_response.role_id,
                    last_login_ip=grpc_response.last_login_ip,
                    created_at=datetime.fromtimestamp(grpc_response.created_at.seconds)
                    if grpc_response.HasField("created_at") else None,
                    updated_at=datetime.fromtimestamp(grpc_response.updated_at.seconds)
                    if grpc_response.HasField("updated_at") else None,
                )
                return CreateUser(user=user_data)
        except grpc.RpcError as e:
            raise Exception(f"gRPC error: {e.details()} (Code: {e.code()})")
        except Exception as ex:
            raise Exception(f"Error occurred while creating user: {str(ex)}")

########################################################################################################################

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    manage_profile = ProfileMutation.Field()
    manage_friendship = FriendshipMutation.Field()
    manage_notification = NotificationMutation.Field()
    manage_setting = SettingMutation.Field()
    manage_user_achievement = UserAchievementMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
